"""Main FastAPI application"""

import logging
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json

from app.config import settings
from app.auth import (
    User,
    UserCreate,
    Token,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin_user,
    get_password_hash,
    verify_admin_password,
    init_default_users,
)
from app.database import db
from app.indexer import indexer_service
from app.rag_service import rag_service
from app.ollama_client import ollama_client


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting application...")
    init_default_users()
    await indexer_service.start()
    logger.info("Application started")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    indexer_service.stop()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Ollama RAG Application",
    description="RAG-powered web application with Ollama integration",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    use_rag: bool = True


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = None


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


class AdminPasswordVerify(BaseModel):
    password: str


# Health check
@app.get("/api/health")
async def health_check():
    """Check application health"""
    ollama_health = await ollama_client.check_health()
    indexer_stats = indexer_service.indexer.get_stats()

    return {
        "status": "healthy",
        "ollama": ollama_health,
        "indexer": {
            "total_documents": indexer_stats.get("total_chunks", 0),
            "indexing_in_progress": indexer_stats.get("indexing_in_progress", False),
        },
    }


# Authentication endpoints
@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing = db.get_user_by_username(user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered"
        )

    # Create user
    hashed_password = get_password_hash(user.password)
    user_id = db.create_user(user.username, hashed_password)

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/login", response_model=Token)
async def login(login_req: LoginRequest):
    """Login and get access token"""
    user = authenticate_user(login_req.username, login_req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# Conversation endpoints
@app.post("/api/conversations")
async def create_conversation(
    conversation: ConversationCreate, current_user: User = Depends(get_current_user)
):
    """Create a new conversation"""
    conversation_id = db.create_conversation(current_user.id, conversation.title)
    return {"id": conversation_id, "title": conversation.title}


@app.get("/api/conversations")
async def list_conversations(current_user: User = Depends(get_current_user)):
    """List all conversations for current user"""
    conversations = db.get_conversations(current_user.id)
    return conversations


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, current_user: User = Depends(get_current_user)):
    """Get a specific conversation with messages"""
    conversation = db.get_conversation_with_messages(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int, current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    success = db.delete_conversation(conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}


@app.get("/api/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: int, current_user: User = Depends(get_current_user)
):
    """Export conversation as JSON"""
    conversation = db.get_conversation_with_messages(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Format for export
    export_data = {
        "conversation_id": conversation["id"],
        "title": conversation["title"],
        "created_at": conversation["created_at"],
        "messages": [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"],
                "sources": msg.get("sources"),
            }
            for msg in conversation["messages"]
        ],
    }

    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": f"attachment; filename=conversation_{conversation_id}.json"},
    )


# Chat endpoints
@app.post("/api/chat")
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """Chat endpoint with streaming response"""

    # Get or create conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = db.create_conversation(current_user.id, "New Conversation")
    else:
        # Verify conversation belongs to user
        conv = db.get_conversation(conversation_id, current_user.id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Get conversation history
    messages = db.get_messages(conversation_id)
    conversation_history = [
        {"role": msg["role"], "content": msg["content"]} for msg in messages
    ]

    # Save user message
    db.add_message(conversation_id, "user", request.message)

    # Streaming response
    async def generate():
        response_parts = []
        sources = []
        first_chunk = True

        try:
            async for chunk, chunk_sources in rag_service.generate_response(
                request.message, conversation_history, use_rag=request.use_rag
            ):
                response_parts.append(chunk)

                if first_chunk and chunk_sources:
                    sources = chunk_sources
                    # Send sources first
                    yield f"data: {json.dumps({'type': 'sources', 'sources': [{'file_name': s['metadata'].get('file_name'), 'text': s['text'][:200] + '...' if len(s['text']) > 200 else s['text']} for s in sources]})}\n\n"
                    first_chunk = False

                # Send content chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"

            # Save assistant response
            full_response = "".join(response_parts)
            db.add_message(conversation_id, "assistant", full_response, sources)

            # Send done signal
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# Search endpoint
@app.post("/api/search")
async def search(request: SearchRequest, current_user: User = Depends(get_current_user)):
    """Search documents without LLM generation"""
    results = await rag_service.search_documents(request.query, top_k=request.top_k)

    # Format results
    formatted_results = [
        {
            "file_name": r["metadata"].get("file_name"),
            "source": r["metadata"].get("source"),
            "text": r["text"],
            "chunk_index": r["metadata"].get("chunk_index"),
            "distance": r.get("distance"),
        }
        for r in results
    ]

    return {"query": request.query, "results": formatted_results}


# Admin endpoints
@app.get("/api/admin/stats")
async def get_admin_stats(current_user: User = Depends(get_current_admin_user)):
    """Get system statistics"""
    indexer_stats = indexer_service.indexer.get_stats()
    ollama_health = await ollama_client.check_health()

    return {
        "indexer": indexer_stats,
        "ollama": ollama_health,
        "users": {"total": len(db.get_user_by_username("admin") and [1] or [])},
    }


@app.post("/api/admin/reindex")
async def trigger_reindex(current_user: User = Depends(get_current_admin_user)):
    """Trigger a full reindex of documents"""
    if indexer_service.indexer.indexing_in_progress:
        raise HTTPException(status_code=400, detail="Indexing already in progress")

    # Start reindexing in background
    import asyncio

    asyncio.create_task(indexer_service.indexer.index_all_documents())

    return {"message": "Reindexing started"}


@app.post("/api/admin/clear-index")
async def clear_index(
    verify: AdminPasswordVerify, current_user: User = Depends(get_current_admin_user)
):
    """Clear all indexed documents (requires admin password)"""
    if not verify_admin_password(verify.password):
        raise HTTPException(status_code=403, detail="Invalid admin password")

    indexer_service.indexer.clear_index()
    return {"message": "Index cleared"}


@app.post("/api/admin/pull-model/{model_name}")
async def pull_model(model_name: str, current_user: User = Depends(get_current_admin_user)):
    """Pull a model from Ollama"""

    async def generate():
        try:
            async for progress in ollama_client.pull_model(model_name):
                yield f"data: {json.dumps(progress)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# Web interface routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin page"""
    return templates.TemplateResponse("admin.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
