# Ollama RAG Web Application

A powerful Retrieval Augmented Generation (RAG) web application that integrates with Ollama for local LLM processing. This application enables users to query and chat with their documents through an intuitive web interface.

## Features

- **Multi-User Support**: Authentication system with user registration and login
- **RAG-Powered Chat**: Ask questions about your documents with context-aware responses
- **Document Processing**: Automatically indexes documents from a knowledge base
  - Supported formats: PDF, Word (.docx), Markdown, HTML, and plain text
- **Streaming Responses**: Real-time streaming of LLM responses
- **Source Attribution**: Shows which documents were used to generate answers
- **Search Mode**: Search documents without LLM generation
- **Conversation Management**: Create, view, and manage multiple conversations
- **Export Functionality**: Export conversations as JSON
- **Admin Dashboard**: Monitor system health, manage indexing, and pull new models
- **Automatic Indexing**: Watches knowledge base folder for changes
- **Vector Database Abstraction**: Supports multiple vector database backends (ChromaDB by default)

## Architecture

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Vanilla JavaScript with modern CSS
- **LLM Provider**: Ollama (llama3.2:3b)
- **Embeddings**: Ollama embeddings (nomic-embed-text)
- **Vector Database**: ChromaDB (with abstraction for other backends)
- **Document Processing**: Multiple format support with chunking
- **Authentication**: JWT-based with secure password hashing

## Prerequisites

- Python 3.11+
- Ollama installed and running
- uv (Python package installer)

Or use Docker:
- Docker
- Docker Compose

## Quick Start with Docker

1. **Clone the repository and navigate to the project directory**:
   ```bash
   cd ollama-client
   ```

2. **Create a `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and set your configuration** (especially `SECRET_KEY` and `ADMIN_PASSWORD`)

4. **Start the services**:
   ```bash
   docker-compose up -d
   ```

5. **Pull the required models**:
   ```bash
   docker exec -it ollama ollama pull llama3.2:3b
   docker exec -it ollama ollama pull nomic-embed-text
   ```

6. **Access the application**:
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Manual Installation

### 1. Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to project directory
cd ollama-client

# Install dependencies
uv pip install -r pyproject.toml
```

### 2. Install and Configure Ollama

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai for installation instructions

# Pull required models
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your configuration
# Important: Change SECRET_KEY and ADMIN_PASSWORD in production!
```

### 4. Add Documents to Knowledge Base

Place your documents (PDF, Word, Markdown, HTML, text files) in the `knowledge-base` folder:

```bash
# The application will automatically index these documents
cp your-documents/* knowledge-base/
```

### 5. Run the Application

```bash
# Start the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or use the main module directly
python app/main.py
```

## Usage

### First Time Setup

1. Navigate to http://localhost:8000
2. Register a new account (first user gets regular access)
3. Login with admin credentials (username: `admin`, password: as set in `.env`)
4. Place documents in the `knowledge-base` folder
5. Documents will be automatically indexed

### Chat Interface

- **Create Conversation**: Click the "+" button in the sidebar
- **Toggle RAG Mode**: Use the switch to enable/disable document retrieval
- **Send Messages**: Type your message and press Ctrl+Enter or click Send
- **View Sources**: Source documents are shown below assistant responses when RAG is enabled
- **Export**: Click Export to download conversation as JSON

### Search Mode

- Click "Search" button to open search modal
- Enter query to search documents without LLM generation
- Results show relevant document chunks with similarity scores

### Admin Panel

Access at http://localhost:8000/admin

Features:
- **System Status**: View Ollama and indexer health
- **Document Statistics**: See number of indexed documents
- **Reindex**: Trigger manual reindexing of all documents
- **Clear Index**: Remove all indexed documents (requires admin password)
- **Model Management**: Pull new Ollama models
- **Detailed Statistics**: View complete system statistics

## Configuration

Edit `.env` file to configure:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Application Settings
SECRET_KEY=your-secret-key-here-change-in-production
ADMIN_PASSWORD=admin123
KNOWLEDGE_BASE_PATH=./knowledge-base

# Vector Database
VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=./data/vectordb

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5

# Server
HOST=0.0.0.0
PORT=8000
```

## Project Structure

```
ollama-client/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── auth.py              # Authentication logic
│   ├── database.py          # SQLite database operations
│   ├── document_processor.py  # Document processing
│   ├── vector_store.py      # Vector database abstraction
│   ├── ollama_client.py     # Ollama API client
│   ├── indexer.py           # Document indexing service
│   └── rag_service.py       # RAG logic
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── admin.js
├── templates/
│   ├── index.html
│   └── admin.html
├── knowledge-base/          # Place your documents here
├── data/                    # Application data (generated)
├── docs/
│   └── design.md           # Design decisions
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Conversations
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/{id}` - Get conversation with messages
- `DELETE /api/conversations/{id}` - Delete conversation
- `GET /api/conversations/{id}/export` - Export conversation

### Chat & Search
- `POST /api/chat` - Send message (streaming)
- `POST /api/search` - Search documents

### Admin
- `GET /api/admin/stats` - Get system statistics
- `POST /api/admin/reindex` - Trigger reindexing
- `POST /api/admin/clear-index` - Clear index
- `POST /api/admin/pull-model/{model}` - Pull Ollama model

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

### Code Formatting

```bash
# Format code
black app/

# Lint code
ruff check app/
```

## Troubleshooting

### Ollama Connection Issues

- Ensure Ollama is running: `ollama serve`
- Check Ollama is accessible: `curl http://localhost:11434/api/tags`
- Verify models are pulled: `ollama list`

### Document Indexing Issues

- Check admin panel for indexing status
- Verify documents are in supported formats
- Check logs for processing errors
- Trigger manual reindex from admin panel

### Permission Issues

- Ensure knowledge-base folder is readable
- Ensure data folder is writable
- Check file permissions in Docker volumes

## Security Considerations

- Change `SECRET_KEY` in production
- Change `ADMIN_PASSWORD` in production
- Use HTTPS in production
- Restrict admin panel access
- Keep dependencies updated
- Review authentication settings

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Acknowledgments

- **Ollama**: For providing local LLM capabilities
- **FastAPI**: For the excellent web framework
- **ChromaDB**: For vector database functionality
- **LangChain**: For document processing utilities
