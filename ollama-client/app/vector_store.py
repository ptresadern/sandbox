"""Vector database abstraction layer"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib

import chromadb
from chromadb.config import Settings as ChromaSettings


class VectorStore(ABC):
    """Abstract base class for vector databases"""

    @abstractmethod
    def add_documents(
        self, texts: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents with embeddings to the store"""
        pass

    @abstractmethod
    def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass

    @abstractmethod
    def delete_by_source(self, source: str) -> int:
        """Delete all documents from a specific source file"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        pass

    @abstractmethod
    def clear(self):
        """Clear all documents from the store"""
        pass


class ChromaVectorStore(VectorStore):
    """ChromaDB implementation of vector store"""

    def __init__(self, persist_directory: Path, collection_name: str = "documents"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(persist_directory),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _generate_id(self, text: str, metadata: Dict[str, Any]) -> str:
        """Generate a unique ID for a document"""
        content = f"{metadata.get('source', '')}_{text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()

    def add_documents(
        self, texts: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents with embeddings to ChromaDB"""
        if not texts:
            return []

        # Generate IDs
        ids = [self._generate_id(text, meta) for text, meta in zip(texts, metadatas)]

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return ids

    def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents in ChromaDB"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                result = {
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                }
                formatted_results.append(result)

        return formatted_results

    def delete_by_source(self, source: str) -> int:
        """Delete all documents from a specific source file"""
        # Get all documents with this source
        results = self.collection.get(where={"source": source})

        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            return len(results["ids"])

        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about ChromaDB"""
        count = self.collection.count()

        # Get unique sources
        all_docs = self.collection.get()
        sources = set()
        if all_docs["metadatas"]:
            sources = {meta.get("source", "") for meta in all_docs["metadatas"]}
            sources.discard("")  # Remove empty sources

        return {
            "total_documents": count,
            "total_chunks": count,
            "unique_sources": len(sources),
            "sources": sorted(list(sources)),
            "backend": "ChromaDB",
        }

    def clear(self):
        """Clear all documents from ChromaDB"""
        # Delete the collection and recreate it
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )


class FAISSVectorStore(VectorStore):
    """FAISS implementation of vector store (placeholder for future implementation)"""

    def __init__(self, persist_directory: Path):
        raise NotImplementedError("FAISS vector store not yet implemented")

    def add_documents(
        self, texts: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> List[str]:
        raise NotImplementedError()

    def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    def delete_by_source(self, source: str) -> int:
        raise NotImplementedError()

    def get_stats(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()


def create_vector_store(db_type: str, persist_directory: Path) -> VectorStore:
    """Factory function to create a vector store"""
    db_type = db_type.lower()

    if db_type == "chroma" or db_type == "chromadb":
        return ChromaVectorStore(persist_directory)
    elif db_type == "faiss":
        return FAISSVectorStore(persist_directory)
    else:
        raise ValueError(f"Unsupported vector database type: {db_type}")
