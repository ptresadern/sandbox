# Ollama RAG Web App - Design Questions

## 1. Ollama/LLM Configuration
- Which Ollama model should be the default? (e.g., llama2, mistral, mixtral)
- Should users be able to switch between different models via the UI?
- Do you want configurable parameters (temperature, context length, etc.)?

**Answers:**
Use llama3.2:3b as the default model
Users do not need to be able to switch
Parameters do not need to be configurable by the user


## 2. RAG Implementation Details
- When you say "different RAG implementations," which specific options do you want?
  - Vector databases: ChromaDB, FAISS, Qdrant, Weaviate?
  - Or different retrieval strategies: semantic search, hybrid search, reranking?
- Which embedding model should be used? (e.g., sentence-transformers, Ollama embeddings)
- Retrieval settings:
  - Chunk size for document splitting? (e.g., 500-1000 tokens)
  - Number of relevant chunks to retrieve? (e.g., top 3-5)

**Answers:**
Just vector databases will do for now
Use the ollama embeddings
500 token chunks
top 5 chunks

## 3. Document Management
- Should indexing be automatic (watches folder for changes) or manual (user triggers)?
- How to handle document updates/deletions?
- Additional file formats beyond text and PDF? (Word docs, markdown, HTML?)
- Should the app track document metadata (title, upload date, tags)?

**Answers:**
Indexing should be automatic
Handle document updates/deletions according to best practices
Please include Word docs, markdown and HTML in the accepted formats
The app needn't track metadata

## 4. Web Frontend Specifics
- Framework preference?
  - **FastAPI** (modern, async, good for APIs)
  - **Flask** (lightweight, simple)
  - **Streamlit/Gradio** (quick prototyping, less customization)
- Features needed:
  - Chat history/conversation memory?
  - Streaming responses (word-by-word)?
  - Show source documents used for each answer?
  - Document upload/management UI?
  - Single user or multi-user support?
  - Authentication required?

**Answers:**
Use FastAPI for the framework
Add a chat history/memory feature
streaming responses are good
do show source documents
no need for a document upload feature at this point
multi-user support, please
authentication required, yes


## 5. Installation & Deployment
- Dependency management preference? (requirements.txt, poetry, pipenv)
- Should I include Docker support?
- Any specific Python version requirement?

**Answers:**
Use uv where possible
Do add docker support
Python 3.11 would be preferred if possible

## 6. Additional Features
- Should there be a "search only" mode (retrieve relevant docs without LLM)?
- Export conversation history?
- Error handling: what should happen if Ollama isn't running or no docs are indexed?

**Answers:**
Do add a "search only" mode
Do add an export feature
The web frontend should provide a password-protected admin page where the model can be restarted and that includes diagnostic information such as the number of documents found/indexed.

---

*Please fill in your answers under each section and let me know when you're ready to proceed with implementation.*
