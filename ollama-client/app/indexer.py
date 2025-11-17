"""Document indexing service with automatic folder watching"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from app.config import settings
from app.document_processor import doc_manager
from app.vector_store import create_vector_store, VectorStore
from app.ollama_client import ollama_client


logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Manages document indexing and vector store operations"""

    def __init__(self, knowledge_base_path: Path = None, vector_store: VectorStore = None):
        self.knowledge_base_path = knowledge_base_path or settings.knowledge_base_path
        self.vector_store = vector_store or create_vector_store(
            settings.vector_db_type, settings.vector_db_path
        )
        self.indexing_in_progress = False
        self.last_index_time: Optional[datetime] = None
        self.index_stats = {"total_files": 0, "successful": 0, "failed": 0, "errors": []}

    async def index_document(self, file_path: Path) -> Dict[str, Any]:
        """Index a single document"""
        logger.info(f"Indexing document: {file_path}")

        result = doc_manager.process_document(
            file_path, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap
        )

        if not result["success"]:
            logger.error(f"Failed to process {file_path}: {result['error']}")
            return result

        # Generate embeddings for chunks
        try:
            embeddings = await ollama_client.embed_batch(result["chunks"])

            # Prepare metadata for each chunk
            metadatas = [
                {
                    "source": str(file_path),
                    "file_name": result["file_name"],
                    "chunk_index": i,
                    "total_chunks": result["num_chunks"],
                }
                for i in range(len(result["chunks"]))
            ]

            # Add to vector store
            ids = self.vector_store.add_documents(
                texts=result["chunks"], metadatas=metadatas, embeddings=embeddings
            )

            logger.info(f"Successfully indexed {file_path} with {len(ids)} chunks")
            result["indexed_chunks"] = len(ids)

        except Exception as e:
            logger.error(f"Failed to index {file_path}: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    async def reindex_document(self, file_path: Path) -> Dict[str, Any]:
        """Reindex a document (delete old chunks and index new ones)"""
        logger.info(f"Reindexing document: {file_path}")

        # Delete existing chunks
        deleted = self.vector_store.delete_by_source(str(file_path))
        if deleted > 0:
            logger.info(f"Deleted {deleted} old chunks from {file_path}")

        # Index the document
        return await self.index_document(file_path)

    async def index_all_documents(self) -> Dict[str, Any]:
        """Index all documents in the knowledge base"""
        if self.indexing_in_progress:
            return {"error": "Indexing already in progress"}

        self.indexing_in_progress = True
        self.index_stats = {"total_files": 0, "successful": 0, "failed": 0, "errors": []}

        logger.info(f"Starting full indexing of {self.knowledge_base_path}")

        try:
            # Process all documents
            results = doc_manager.process_directory(
                self.knowledge_base_path,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap,
            )

            self.index_stats["total_files"] = len(results)

            # Index each document
            for result in results:
                if result["success"]:
                    try:
                        # Generate embeddings
                        embeddings = await ollama_client.embed_batch(result["chunks"])

                        # Prepare metadata
                        metadatas = [
                            {
                                "source": result["file_path"],
                                "file_name": result["file_name"],
                                "chunk_index": i,
                                "total_chunks": result["num_chunks"],
                            }
                            for i in range(len(result["chunks"]))
                        ]

                        # Add to vector store (this will replace if exists due to ID generation)
                        # First delete old chunks
                        self.vector_store.delete_by_source(result["file_path"])

                        # Add new chunks
                        self.vector_store.add_documents(
                            texts=result["chunks"], metadatas=metadatas, embeddings=embeddings
                        )

                        self.index_stats["successful"] += 1
                        logger.info(f"Successfully indexed {result['file_name']}")

                    except Exception as e:
                        self.index_stats["failed"] += 1
                        error_msg = f"{result['file_name']}: {str(e)}"
                        self.index_stats["errors"].append(error_msg)
                        logger.error(f"Failed to index {result['file_name']}: {e}")
                else:
                    self.index_stats["failed"] += 1
                    error_msg = f"{result['file_name']}: {result['error']}"
                    self.index_stats["errors"].append(error_msg)

            self.last_index_time = datetime.utcnow()

        finally:
            self.indexing_in_progress = False

        logger.info(
            f"Indexing complete: {self.index_stats['successful']}/{self.index_stats['total_files']} successful"
        )

        return self.index_stats

    async def search(self, query: str, top_k: int = None) -> list[Dict[str, Any]]:
        """Search for relevant documents"""
        top_k = top_k or settings.top_k_results

        # Generate query embedding
        query_embedding = await ollama_client.embed(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        vector_stats = self.vector_store.get_stats()

        return {
            **vector_stats,
            "indexing_in_progress": self.indexing_in_progress,
            "last_index_time": self.last_index_time.isoformat() if self.last_index_time else None,
            "last_index_stats": self.index_stats,
        }

    def clear_index(self):
        """Clear all indexed documents"""
        self.vector_store.clear()
        logger.info("Cleared all indexed documents")


class KnowledgeBaseWatcher(FileSystemEventHandler):
    """Watch knowledge base folder for changes"""

    def __init__(self, indexer: DocumentIndexer):
        self.indexer = indexer
        self.debounce_delay = 2.0  # seconds
        self.pending_files: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self._schedule_index(Path(event.src_path))

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self._schedule_index(Path(event.src_path))

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            asyncio.create_task(self._handle_deletion(Path(event.src_path)))

    def _schedule_index(self, file_path: Path):
        """Schedule a file for indexing with debouncing"""
        if doc_manager.can_process(file_path):
            # Debounce: schedule indexing after delay
            asyncio.create_task(self._debounced_index(file_path))

    async def _debounced_index(self, file_path: Path):
        """Index file after debounce delay"""
        await asyncio.sleep(self.debounce_delay)

        try:
            await self.indexer.reindex_document(file_path)
        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")

    async def _handle_deletion(self, file_path: Path):
        """Handle file deletion"""
        try:
            deleted = self.indexer.vector_store.delete_by_source(str(file_path))
            if deleted > 0:
                logger.info(f"Deleted {deleted} chunks for removed file: {file_path}")
        except Exception as e:
            logger.error(f"Error handling deletion of {file_path}: {e}")


class IndexerService:
    """Service to manage automatic indexing"""

    def __init__(self):
        self.indexer = DocumentIndexer()
        self.watcher = KnowledgeBaseWatcher(self.indexer)
        self.observer: Optional[Observer] = None

    async def start(self):
        """Start the indexer service"""
        logger.info("Starting indexer service...")

        # Initial indexing
        await self.indexer.index_all_documents()

        # Start watching for changes
        self.observer = Observer()
        self.observer.schedule(
            self.watcher, str(settings.knowledge_base_path), recursive=True
        )
        self.observer.start()

        logger.info("Indexer service started")

    def stop(self):
        """Stop the indexer service"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logger.info("Indexer service stopped")


# Global indexer service instance
indexer_service = IndexerService()
