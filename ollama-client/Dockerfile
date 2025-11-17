FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy requirements file
COPY requirements.txt ./

# Install dependencies with uv
RUN uv pip install --system -r requirements.txt

# Copy application files
COPY app ./app
COPY static ./static
COPY templates ./templates

# Create necessary directories
RUN mkdir -p /app/data /app/knowledge-base

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
