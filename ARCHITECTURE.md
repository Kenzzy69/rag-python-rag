# Architecture Documentation

## System Overview

This RAG system implements a two-phase architecture:
1. **Indexing Phase**: Process documents into searchable vectors (one-time or periodic)
2. **Query Phase**: Retrieve relevant context and generate answers (per-request)

## Core Components

### 1. Document Converter (`document_converter.py`)

**Responsibility**: Transform various document formats into plain text.

**Supported Formats**:
- PDF → PyMuPDF (fitz)
- DOCX → python-docx
- TXT → direct read

**Process**:
```
Input: documents/*.{pdf,docx,txt}
  ↓
Extract text with formatting preservation
  ↓
Output: processed_docs/*.md
```

**Key Functions**:
- `convert_pdf_to_markdown()`: Extracts text page-by-page
- `convert_docx_to_markdown()`: Preserves paragraph structure
- `convert_all_documents()`: Batch processing

**Limitations**:
- Images are ignored
- Tables may lose structure
- Complex layouts flatten to linear text

---

### 2. Text Splitter (`text_splitter.py`)

**Responsibility**: Divide documents into semantic chunks with overlap.

**Strategy**: LangChain's `RecursiveCharacterTextSplitter`

**Parameters**:
- `chunk_size`: 1000 characters (configurable)
- `chunk_overlap`: 200 characters (preserves context across boundaries)
- `separators`: `["\n\n", "\n", ". ", " ", ""]` (hierarchical splitting)

**Process**:
```
Input: processed_docs/*.md
  ↓
Split on paragraph boundaries first
  ↓
If chunk > 1000 chars, split on sentences
  ↓
If still too large, split on words
  ↓
Output: List[Document] with metadata
```

**Metadata Attached**:
- Source file path
- Chunk index
- Original document title

**Why Overlap Matters**:
- Prevents context loss at chunk boundaries
- Improves retrieval for queries spanning multiple chunks

---

### 3. Vector Store (`vector_store.py`)

**Responsibility**: Store embeddings and perform similarity search.

**Technology**: ChromaDB (persistent, local-first vector database)

**Embedding Model**: `all-MiniLM-L6-v2` (sentence-transformers)
- Dimensions: 384
- Speed: ~1000 sentences/sec on CPU
- Language: Primarily English (degraded performance on other languages)

**Process**:
```
Input: List[Document] chunks
  ↓
Generate embeddings via SentenceTransformer
  ↓
Store in ChromaDB collection with metadata
  ↓
Index: HNSW (Hierarchical Navigable Small World)
```

**Query Flow**:
```
User question (text)
  ↓
Generate query embedding
  ↓
Cosine similarity search in ChromaDB
  ↓
Return top-k chunks (default: 5)
```

**Key Methods**:
- `add_documents()`: Batch insert with embeddings
- `retrieve_context()`: Similarity search
- `get_collection_stats()`: Metadata and count

**Distance Metric**: Cosine similarity (default)

---

### 4. LLM Handler (`llm_handler.py`)

**Responsibility**: Generate answers using local LLM via Ollama.

**Model**: `llama3.2` (default, 3B parameters)

**Process**:
```
Input: Question + Retrieved context
  ↓
Format prompt template
  ↓
Send to Ollama API (localhost:11434)
  ↓
Stream response tokens
  ↓
Output: Generated answer
```

**Prompt Template**:
```
You are a helpful assistant. Answer the question based on the context provided.

Context: {retrieved_chunks}

Question: {user_question}

Answer:
```

**Streaming vs Synchronous**:
- **Streaming** (`stream_llm_answer()`): Yields tokens as generated (better UX)
- **Synchronous** (`generate_answer()`): Returns complete answer (simpler API)

**Error Handling**:
- Model availability check before inference
- Timeout after 60 seconds
- Fallback to error message if Ollama unreachable

---

### 5. Main Application (`main.py`)

**Responsibility**: Orchestrate pipeline and launch web interface.

**Initialization Sequence**:
```
1. Load configuration
2. Download test document (if first run)
3. Convert documents to markdown
4. Split into chunks
5. Initialize vector store
6. Check if documents already indexed
7. If not, add embeddings to ChromaDB
8. Verify Ollama model availability
9. Launch Gradio interface
```

**RAGSystem Class**:
- `setup_pipeline()`: Runs indexing phase
- `query()`: Handles user questions (retrieval + generation)

**Gradio Interface**:
- Input: Text box for questions
- Output: Markdown with answer + sources
- Examples: Pre-defined questions
- Theme: Gradio default (configurable)

---

## Data Flow

### Indexing Phase (One-Time)

```
┌─────────────┐
│  Documents  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Document Converter  │  ← PyMuPDF, python-docx
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Text Splitter     │  ← LangChain
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Embedding Generator │  ← sentence-transformers
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│     ChromaDB        │  ← Persistent storage
└─────────────────────┘
```

**Time Complexity**: O(n) where n = number of chunks (~30 seconds for 847 chunks)

---

### Query Phase (Per-Request)

```
┌──────────────┐
│ User Question│
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Embedding Generator │  ← Same model as indexing
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  ChromaDB Search    │  ← Cosine similarity
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Top-k Chunks       │  ← Default: 5 chunks
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Prompt Formatter   │  ← Inject context
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Ollama (LLM)      │  ← llama3.2 inference
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Answer + Sources   │
└─────────────────────┘
```

**Time Complexity**: 
- Embedding: ~50ms
- Search: ~100ms
- LLM inference: 5-15 seconds (depends on answer length)

---

## Configuration Management

**File**: `config.py`

**Key Parameters**:
```python
# Paths
DOCUMENTS_DIR = "./documents"
CHROMA_DB_DIR = "./chroma_db"

# Models
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
OLLAMA_MODEL_NAME = "llama3.2"

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval
DEFAULT_N_RESULTS = 5

# LLM
LLM_TEMPERATURE = 0.7
```

**Environment Variables** (`.env`):
- Override config.py values
- Useful for deployment-specific settings
- Not committed to Git

---

## Synchronous vs Asynchronous

**Current Implementation**: Synchronous

- Document processing: Sequential
- Embedding generation: Batch (but blocking)
- LLM inference: Streaming (but single-threaded)

**Implications**:
- Only one query processed at a time
- Gradio queues requests automatically
- No concurrent document indexing

**Future Improvement**:
- Use `asyncio` for concurrent queries
- Background task for document re-indexing
- WebSocket for real-time streaming

---

## Memory Management

**RAM Usage Breakdown**:
- Embedding model: ~500MB
- ChromaDB index: ~100MB per 1000 chunks
- Ollama model: ~2-4GB (depends on model size)
- Python overhead: ~200MB

**Total**: 4-6GB minimum

**Optimization Strategies**:
- Lazy load embedding model (only when needed)
- Use quantized Ollama models (Q4, Q5)
- Limit ChromaDB collection size (delete old documents)

---

## Error Handling

**Graceful Degradation**:
1. If Ollama unavailable → Show error message (don't crash)
2. If document conversion fails → Skip file, log error
3. If embedding generation fails → Retry once, then skip
4. If ChromaDB locked → Wait and retry (up to 3 times)

**Logging**:
- All components use Python `logging` module
- Levels: INFO (default), DEBUG (verbose), ERROR (critical)
- Output: Console (can redirect to file)

---

## Testing Strategy

**Unit Tests** (not implemented):
- `test_document_converter.py`: Verify PDF/DOCX parsing
- `test_text_splitter.py`: Check chunk sizes and overlap
- `test_vector_store.py`: Validate embedding dimensions
- `test_llm_handler.py`: Mock Ollama responses

**Integration Tests** (manual):
- Run `python main.py` and verify startup
- Query known document and check answer accuracy
- Test with non-English queries

**Performance Tests**:
- Measure indexing time for various document sizes
- Benchmark query latency under load

---

## Scalability Considerations

**Current Limitations**:
- Single-machine deployment
- No horizontal scaling
- In-memory embeddings (ChromaDB limitation)

**Scaling Strategies**:
1. **Vertical Scaling**: Add more RAM/CPU
2. **Model Optimization**: Use smaller/quantized models
3. **Caching**: Store frequent query results
4. **Distributed ChromaDB**: Use client-server mode
5. **Load Balancing**: Multiple Ollama instances behind nginx

**When to Scale**:
- \>10,000 documents
- \>100 concurrent users
- \>1M chunks in vector store

---

## Security Architecture

**Current State**: No authentication or authorization

**Threat Model**:
- Malicious document upload (XSS, code injection)
- Prompt injection attacks
- Resource exhaustion (DoS)
- Data exfiltration via queries

**Mitigation Strategies** (not implemented):
- Sandboxed document processing
- Input sanitization
- Rate limiting per IP
- Query result filtering

**See**: `LIMITATIONS.md` for production readiness gaps

---

## Alternative Architectures

### Option 1: API-First Design

Replace Gradio with FastAPI:
```
Frontend (Vue.js) → REST API (FastAPI) → RAG Backend
```

**Benefits**:
- Decoupled UI/backend
- Mobile app support
- Better caching

### Option 2: Serverless

Use AWS Lambda + S3 + Pinecone:
```
S3 (docs) → Lambda (indexing) → Pinecone (vectors)
API Gateway → Lambda (query) → OpenAI API
```

**Benefits**:
- Auto-scaling
- Pay-per-use
- No server management

**Drawbacks**:
- Higher latency
- Vendor lock-in
- Cost at scale

---

## Performance Benchmarks

**Test Document**: Think Python (300 pages, 847 chunks)

| Operation | Time | Notes |
|-----------|------|-------|
| PDF Conversion | 5s | PyMuPDF |
| Text Splitting | 2s | LangChain |
| Embedding Generation | 20s | CPU, batch=32 |
| ChromaDB Indexing | 3s | Disk write |
| Query Embedding | 50ms | Single query |
| Vector Search | 100ms | 847 chunks |
| LLM Inference | 8s | llama3.2, ~100 tokens |
| **Total Query Time** | **~8-10s** | End-to-end |

**Hardware**: M1 MacBook Pro, 16GB RAM

---

## Future Architecture Improvements

1. **Hybrid Search**: Combine vector search with keyword search (BM25)
2. **Re-ranking**: Use cross-encoder to re-rank top-k results
3. **Multi-hop Reasoning**: Chain multiple queries for complex questions
4. **Document Metadata**: Filter by date, author, document type
5. **Conversation Memory**: Track dialogue context across queries

---

**Status**: Current architecture suitable for prototyping and small-scale deployments (<1000 documents, <10 concurrent users).
