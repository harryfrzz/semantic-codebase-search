FROM golang:1.24-alpine AS go-builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY main_cli.go ./
RUN go build -o codebase-search main_cli.go

# Second stage: Python runtime with Go binary
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Note: HF_TOKEN should be passed at runtime with -e flag for security

# Install system dependencies including curl for Ollama
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set work directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY core_main/requirements.txt ./core_main/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r ./core_main/requirements.txt

# Copy Python source code to a fixed location
COPY core_main/ /app/core_main/

# Copy Go binary from builder stage
COPY --from=go-builder /app/codebase-search /usr/local/bin/codebase-search

# Make the Go binary executable
RUN chmod +x /usr/local/bin/codebase-search

# Create workspace directory for mounting external codebases
RUN mkdir -p /workspace

# Copy startup script and test script
COPY start-ollama.sh /usr/local/bin/start-ollama.sh
COPY test-setup.sh /usr/local/bin/test-setup.sh
RUN chmod +x /usr/local/bin/start-ollama.sh /usr/local/bin/test-setup.sh

# Set workspace as working directory (for analyzing mounted codebases)
WORKDIR /workspace

# Expose ports (Ollama uses 11434, your app might use 8000)
EXPOSE 8000 11434

# Default command runs the startup script
CMD ["/usr/local/bin/start-ollama.sh"]

