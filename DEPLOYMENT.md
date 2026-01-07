# Deployment Guide

## Overview

This RAG system is a **Python backend application** that requires:
- Python runtime (3.9+)
- Ollama service running locally or remotely
- Persistent storage for ChromaDB
- 4GB+ RAM

It **cannot** be deployed as a static site.

## Why GitHub Pages Doesn't Work

GitHub Pages serves static HTML/CSS/JS files only. This project requires:
- Python interpreter
- Long-running processes (Ollama, ChromaDB)
- Server-side document processing
- Dynamic request handling

**Verdict**: GitHub Pages is incompatible with this architecture.

## Supported Deployment Options

### 1. Local Development (Recommended for Testing)

**Pros**:
- Full control
- No cost
- Fast iteration
- Privacy (documents stay local)

**Cons**:
- Not accessible remotely
- Requires manual setup

**Setup**:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Run application
python main.py
```

Access at: `http://localhost:7860`

---

### 2. Hugging Face Spaces (Best for Demos)

**Pros**:
- Free tier available
- Gradio native support
- Public URL
- No server management

**Cons**:
- CPU-only (slow inference)
- Limited RAM (7GB max on free tier)
- Ephemeral storage (documents reset on restart)
- Cold start delays

**Requirements**:
- Create `app.py` (rename `main.py`)
- Add `requirements.txt`
- Configure Spaces to use Gradio SDK
- **Important**: Ollama must run in same container or use external endpoint

**Limitations**:
- Ollama models are large (~4GB for llama3.2)
- May exceed free tier storage
- Consider using smaller models (e.g., `llama3.2:1b`)

**Example `README.md` for Spaces**:
```yaml
---
title: RAG Document QA
emoji: 📚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
---
```

---

### 3. Cloud Platforms (Production-Ready)

#### Render

**Pros**:
- Persistent storage
- Custom Docker support
- Automatic deployments from Git

**Cons**:
- Paid plans required for sufficient resources
- ~$7/month minimum for 1GB RAM

**Setup**:
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: rag-system
    runtime: python3
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: OLLAMA_HOST
        value: http://localhost:11434
```

2. Add Ollama as separate service or use external endpoint

---

#### Fly.io

**Pros**:
- Generous free tier
- Global edge deployment
- Docker-based

**Cons**:
- Requires Dockerfile
- Complex setup for multi-service apps

**Setup**:
```dockerfile
FROM python:3.9-slim

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy application
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Start Ollama and app
CMD ollama serve & python main.py
```

---

#### Railway

**Pros**:
- Simple Git integration
- Automatic HTTPS
- Database support

**Cons**:
- Free tier limited to 500 hours/month
- Resource constraints on free tier

**Setup**:
- Connect GitHub repository
- Set environment variables
- Deploy from `main` branch

---

### 4. Docker (Self-Hosted)

**Best for**: VPS, home server, enterprise deployment

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Expose Gradio port
EXPOSE 7860

# Start services
CMD ["sh", "-c", "ollama serve & sleep 5 && ollama pull llama3.2 && python main.py"]
```

**Docker Compose**:
```yaml
version: '3.8'

services:
  rag-system:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - ./documents:/app/documents
      - ./chroma_db:/app/chroma_db
    environment:
      - OLLAMA_HOST=http://localhost:11434
```

---

## Deployment Checklist

Before deploying, ensure:

- [ ] Ollama is accessible (local or remote endpoint)
- [ ] Required model is pulled (`llama3.2` or alternative)
- [ ] Environment variables are set (see `.env.example`)
- [ ] Sufficient RAM available (4GB minimum, 8GB recommended)
- [ ] Persistent storage configured for `chroma_db/`
- [ ] Documents directory is populated or upload mechanism exists
- [ ] Security considerations addressed (see below)

## Security Considerations

This application is **not production-hardened**. Before public deployment:

1. **Add Authentication**
   - Gradio supports basic auth: `demo.launch(auth=("username", "password"))`
   - Consider OAuth for multi-user scenarios

2. **Rate Limiting**
   - Implement request throttling
   - Prevent abuse of LLM inference

3. **Input Validation**
   - Sanitize uploaded documents
   - Limit file sizes and types

4. **Network Security**
   - Use HTTPS (reverse proxy with nginx/Caddy)
   - Restrict Ollama endpoint access

5. **Resource Limits**
   - Set memory limits in Docker
   - Implement query timeouts

## Performance Optimization

For production deployments:

1. **Use GPU Acceleration**
   - Ollama supports CUDA/ROCm
   - 10-50x faster inference

2. **Caching**
   - Cache embeddings for frequently accessed documents
   - Implement query result caching

3. **Model Selection**
   - Smaller models (1B-3B params) for faster responses
   - Quantized models (Q4, Q5) for reduced memory

4. **Horizontal Scaling**
   - Run multiple Ollama instances
   - Load balance with nginx

## Cost Estimates

| Platform | Free Tier | Paid (Minimum) | Notes |
|----------|-----------|----------------|-------|
| Local | $0 | $0 | Electricity costs only |
| HF Spaces | Limited | $0 | CPU-only, slow |
| Render | No | ~$7/month | 1GB RAM insufficient |
| Fly.io | 500hrs | ~$5/month | Requires optimization |
| Railway | 500hrs | ~$5/month | Good for demos |
| VPS (Hetzner) | No | ~$5/month | Full control |

## Monitoring

Recommended monitoring for production:

- **Application Logs**: Track query latency, errors
- **Resource Usage**: RAM, CPU, disk I/O
- **Ollama Metrics**: Model load time, inference speed
- **ChromaDB Stats**: Collection size, query performance

## Backup Strategy

Critical data to backup:
- `chroma_db/` - Vector database
- `documents/` - Source documents
- `config.py` - Configuration
- `.env` - Environment variables (encrypted)

## Troubleshooting Deployments

### Issue: Ollama connection refused

**Solution**: Ensure Ollama is running before application starts
```bash
# Add to startup script
ollama serve &
sleep 5  # Wait for Ollama to initialize
python main.py
```

### Issue: Out of memory

**Solution**: Reduce model size or increase RAM
```python
# Use smaller model
OLLAMA_MODEL_NAME = "llama3.2:1b"

# Reduce chunk retrieval
DEFAULT_N_RESULTS = 3
```

### Issue: Slow cold starts

**Solution**: Keep models pre-loaded
```bash
# In Dockerfile
RUN ollama pull llama3.2
```

## Alternative: API-Only Deployment

For advanced users, deploy as REST API instead of Gradio:

1. Replace Gradio with FastAPI
2. Create separate frontend (Vue.js, React)
3. Deploy frontend to Vercel/Netlify
4. Deploy backend to Render/Fly.io

See `ARCHITECTURE.md` for API design considerations.

---

**Recommendation**: Start with local deployment, then move to Hugging Face Spaces for demos, and finally to Render/Fly.io for production.
