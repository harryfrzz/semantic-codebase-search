# Semantic Codebase Search

A simple tool for semantic code search using local AI models and embeddings.

## Tech Stack
- **Python** (core logic)
- **Go** (optional CLI)
- **Ollama** (local LLM inference)
- **FAISS** (vector search)
- **LangChain** (embeddings)

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/harryfrzz/semantic-codebase-search.git
cd semantic-codebase-search
```

### 2. Install Go (for CLI, optional)
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install -y golang-go

# Check Go version
go version
```

### 3. Install Python dependencies
```bash
# Make sure you have Python 3.11+
# Install all Python dependencies
pip install -r core_main/requirements.txt
```

### 4. Install Ollama and Pull Models
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama (in background)
ollama serve &

# Pull required models
ollama pull all-minilm:33m
ollama pull gpt-oss:20b
```

## Usage

### Python Script
```bash
python3 core_main/entry_point.py "your search query here"
```

### Go CLI (optional)
```bash
# Build the CLI
go build -o semantic-search main_cli.go

# Run the CLI
./semantic-search

# Or
go run main_cli.go
```
