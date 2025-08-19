FROM golang:1.24-bullseye AS go-builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY main_cli.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o codebase-search main_cli.go

FROM python:3.11-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm-256color
ENV COLORTERM=truecolor

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create directories
RUN mkdir -p /app/core_main /workspace
WORKDIR /workspace

# Copy Python requirements and install
COPY core_main/requirements.txt /app/core_main/
RUN pip install --no-cache-dir -r /app/core_main/requirements.txt

# Copy Python code
COPY core_main/ /app/core_main/

# Copy Go binary
COPY --from=go-builder /app/codebase-search /usr/local/bin/codebase-search
RUN chmod +x /usr/local/bin/codebase-search

# Copy startup script
COPY start-ollama.sh /app/
RUN chmod +x /app/start-ollama.sh

# Pre-download Ollama models during build
RUN ollama serve & \
    sleep 10 && \
    ollama pull all-minilm:33m && \
    pkill ollama

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 11434 8000

CMD ["/app/start-ollama.sh"]

