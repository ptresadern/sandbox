"""RAG (Retrieval Augmented Generation) service"""

from typing import List, Dict, Any, AsyncGenerator
import logging

from app.indexer import indexer_service
from app.ollama_client import ollama_client
from app.config import settings


logger = logging.getLogger(__name__)


class RAGService:
    """Service for Retrieval Augmented Generation"""

    def __init__(self):
        self.indexer = indexer_service.indexer

    async def search_documents(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents without LLM generation"""
        results = await self.indexer.search(query, top_k=top_k)
        return results

    def _format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results into context for the LLM"""
        if not search_results:
            return "No relevant documents found."

        context_parts = []
        for i, result in enumerate(search_results, 1):
            source = result["metadata"].get("file_name", "Unknown")
            text = result["text"]
            context_parts.append(f"[Source {i}: {source}]\n{text}")

        return "\n\n".join(context_parts)

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create a prompt that includes retrieved context"""
        return f"""Based on the following context from the knowledge base, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, please say so."""

    async def generate_response(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
        use_rag: bool = True,
        top_k: int = None,
    ) -> AsyncGenerator[tuple[str, List[Dict[str, Any]]], None]:
        """
        Generate a response using RAG

        Yields tuples of (text_chunk, sources)
        The sources list is only populated in the first yield
        """
        sources = []

        if use_rag:
            # Search for relevant documents
            search_results = await self.search_documents(query, top_k=top_k)
            sources = search_results

            if search_results:
                # Format context
                context = self._format_context(search_results)

                # Create RAG prompt
                rag_prompt = self._create_rag_prompt(query, context)

                # Build messages for chat
                messages = conversation_history or []
                messages.append({"role": "user", "content": rag_prompt})

            else:
                # No relevant documents found
                messages = conversation_history or []
                messages.append(
                    {
                        "role": "user",
                        "content": f"{query}\n\nNote: No relevant documents were found in the knowledge base.",
                    }
                )
        else:
            # No RAG, just direct chat
            messages = conversation_history or []
            messages.append({"role": "user", "content": query})

        # Generate response with streaming
        first_chunk = True
        async for chunk in ollama_client.chat(messages, stream=True):
            if first_chunk:
                # Include sources with first chunk
                yield (chunk, sources)
                first_chunk = False
            else:
                yield (chunk, [])

    async def generate_simple_response(self, query: str, use_rag: bool = True) -> Dict[str, Any]:
        """
        Generate a complete response (non-streaming version)

        Returns dict with 'response' and 'sources'
        """
        response_parts = []
        sources = []

        async for chunk, chunk_sources in self.generate_response(query, use_rag=use_rag):
            response_parts.append(chunk)
            if chunk_sources and not sources:
                sources = chunk_sources

        return {"response": "".join(response_parts), "sources": sources}


# Global RAG service instance
rag_service = RAGService()
