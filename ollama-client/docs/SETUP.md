# Setup Guide

## Detailed Setup Instructions

### Prerequisites

1. **Python 3.11 or higher**
   ```bash
   python --version  # Should show 3.11+
   ```

2. **Ollama**
   - Visit https://ollama.ai
   - Download and install for your platform
   - Start Ollama service

3. **uv (Python package installer)**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Installation Steps

#### Option 1: Docker (Recommended)

1. **Install Docker and Docker Compose**
   - Docker Desktop (Mac/Windows): https://www.docker.com/products/docker-desktop
   - Docker Engine (Linux): https://docs.docker.com/engine/install/

2. **Clone and setup**
   ```bash
   cd ollama-client
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Pull models**
   ```bash
   docker exec -it ollama ollama pull llama3.2:3b
   docker exec -it ollama ollama pull nomic-embed-text
   ```

5. **Access application**
   - Main app: http://localhost:8000
   - Admin: http://localhost:8000/admin

#### Option 2: Manual Installation

1. **Install dependencies**
   ```bash
   cd ollama-client
   uv pip install -r pyproject.toml
   ```

2. **Setup Ollama**
   ```bash
   # Start Ollama (if not running)
   ollama serve &

   # Pull required models
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

4. **Run application**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Initial Configuration

1. **Set Secret Key** (Production)
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   # Add to .env as SECRET_KEY
   ```

2. **Set Admin Password**
   ```bash
   # Edit .env
   ADMIN_PASSWORD=your-secure-password
   ```

3. **Add Documents**
   ```bash
   # Copy your documents to knowledge-base folder
   cp /path/to/your/documents/* knowledge-base/
   ```

### Verification

1. **Check Ollama**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Check Application Health**
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Login to Admin Panel**
   - Navigate to http://localhost:8000/admin
   - Login with admin credentials
   - Check system status

### Troubleshooting

#### Ollama not connecting

```bash
# Check if Ollama is running
ps aux | grep ollama

# Check port
netstat -an | grep 11434

# Restart Ollama
killall ollama
ollama serve
```

#### Models not found

```bash
# List installed models
ollama list

# Pull missing models
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

#### Permission errors

```bash
# Fix data directory permissions
chmod -R 755 data/
chmod -R 755 knowledge-base/
```

#### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process or change PORT in .env
PORT=8080
```

### Production Deployment

1. **Use reverse proxy (nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Enable HTTPS**
   - Use Let's Encrypt for SSL certificates
   - Configure nginx for HTTPS

3. **Use systemd service**
   ```bash
   # Create /etc/systemd/system/ollama-rag.service
   [Unit]
   Description=Ollama RAG Web App
   After=network.target

   [Service]
   Type=simple
   User=youruser
   WorkingDirectory=/path/to/ollama-client
   Environment="PATH=/usr/local/bin:/usr/bin:/bin"
   ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and start**
   ```bash
   sudo systemctl enable ollama-rag
   sudo systemctl start ollama-rag
   ```

### Upgrading

1. **Backup data**
   ```bash
   cp -r data/ data.backup/
   ```

2. **Pull latest changes**
   ```bash
   git pull origin main
   ```

3. **Update dependencies**
   ```bash
   uv pip install -r pyproject.toml --upgrade
   ```

4. **Restart application**
   ```bash
   # Docker
   docker-compose restart web

   # Manual
   sudo systemctl restart ollama-rag
   ```

### Performance Tuning

1. **Increase chunk size** for longer context
   ```env
   CHUNK_SIZE=1000
   ```

2. **Adjust top-k results** for relevance
   ```env
   TOP_K_RESULTS=3
   ```

3. **Use different models** for better performance
   ```env
   OLLAMA_MODEL=llama2:13b
   ```

### Monitoring

1. **Check logs**
   ```bash
   # Docker
   docker-compose logs -f web

   # Systemd
   journalctl -u ollama-rag -f
   ```

2. **Monitor resources**
   ```bash
   # Docker
   docker stats

   # System
   htop
   ```

3. **Admin dashboard**
   - Access http://localhost:8000/admin
   - Monitor system health
   - Check indexing status
