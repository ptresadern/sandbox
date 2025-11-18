"""Ollama client for LLM and embeddings"""

import httpx
from typing import List, Dict, Any, AsyncGenerator, Optional
import json

from app.config import settings


class OllamaClient:
    """Client for interacting with Ollama API"""

    def __init__(self, base_url: str = None, model: str = None, embedding_model: str = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.embedding_model = embedding_model or settings.ollama_embedding_model
        # Increased timeout for RAG requests with large context
        self.timeout = httpx.Timeout(300.0, connect=10.0, read=300.0)

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Generate text from Ollama with streaming support"""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": temperature},
        }

        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Chat with Ollama using conversation history with streaming support"""
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        url = f"{self.base_url}/api/embeddings"

        payload = {"model": self.embedding_model, "prompt": text}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)
        return embeddings

    async def check_health(self) -> Dict[str, Any]:
        """Check if Ollama is running and accessible"""
        try:
            url = f"{self.base_url}/api/tags"
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                # Check if our models are available
                models = [model["name"] for model in data.get("models", [])]
                has_llm = any(self.model in m for m in models)
                has_embedding = any(self.embedding_model in m for m in models)

                return {
                    "status": "healthy",
                    "available_models": models,
                    "llm_model": self.model,
                    "llm_available": has_llm,
                    "embedding_model": self.embedding_model,
                    "embedding_available": has_embedding,
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "llm_model": self.model,
                "llm_available": False,
                "embedding_model": self.embedding_model,
                "embedding_available": False,
            }

    async def pull_model(self, model_name: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Pull a model from Ollama (with progress updates)"""
        url = f"{self.base_url}/api/pull"
        payload = {"name": model_name, "stream": True}

        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            continue


# Global Ollama client instance
ollama_client = OllamaClient()
