# RAG System - Intelligent Document Q&A

A complete RAG (Retrieval-Augmented Generation) system for intelligent document search and question answering using local LLM models.

## 🌟 Features

- 📄 **Document Conversion**: Automatic conversion of PDF, DOCX, TXT files to markdown
- 🧩 **Smart Splitting**: Text chunking with context preservation (LangChain)
- 🔍 **Vector Search**: Fast semantic search across documents (ChromaDB)
- 🤖 **Local LLM**: Answer generation using Ollama (no cloud data transfer)
- 🌐 **Web Interface**: User-friendly Gradio interface with streaming responses
- 🌍 **Multilingual**: Support for English, Russian, and Ukrainian languages

## 🏗️ Architecture

```
Documents → Conversion (PyMuPDF) → Splitting (LangChain)
                                           ↓
User Question → Search (ChromaDB) → Context + Question
                                           ↓
                                 LLM (Ollama llama3.2)
                                           ↓
                                 Answer + Sources
```

## 📋 Requirements

- Python 3.9+
- Ollama (for local LLM model execution)
- 4+ GB RAM (for embedding model and LLM)

## 🚀 Installation

### 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# After installation, download the model
ollama pull llama3.2
```

### 2. Clone and Setup Project

```bash
# Navigate to project directory
cd /Users/v.hirenko/Desktop/DevHubVault/my-ai-projects/rag-python-rag

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## 📚 Project Structure

```
rag-python-rag/
├── config.py                # System configuration
├── document_converter.py    # Document conversion
├── text_splitter.py        # Text chunking
├── vector_store.py         # Vector storage
├── llm_handler.py          # LLM request handling
├── main.py                 # Main application
├── requirements.txt        # Dependencies
├── documents/              # Source documents
├── processed_docs/         # Converted documents
└── chroma_db/             # Vector database
```

## 🎯 Usage

### Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python main.py
```

The application will automatically:

1. Download test document (Think Python PDF)
2. Convert it to markdown
3. Split into chunks
4. Create vector database
5. Launch web interface at http://localhost:7860

### Adding Your Own Documents

1. Place documents (PDF, DOCX, TXT) in the `documents/` folder
2. Restart the application or run indexing:

```bash
python -c "
from main import RAGSystem
rag = RAGSystem()
rag.setup_pipeline(force_rebuild=True)
"
```

### Using Python API

```python
from vector_store import retrieve_context
from llm_handler import generate_answer, format_response

# Ask a question
question = "How do loops work in Python?"

# Get context from documents
context, sources = retrieve_context(question, n_results=5)

# Generate answer
answer = generate_answer(question, context)

# Format result
response = format_response(question, answer, sources)
print(response)
```

### Streaming Answer Generation

```python
from vector_store import retrieve_context
from llm_handler import stream_llm_answer

question = "What are Python functions?"
context, sources = retrieve_context(question)

# Stream output
for token in stream_llm_answer(question, context):
    print(token, end='', flush=True)
```

## ⚙️ Configuration

Main settings are in `config.py`:

```python
# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# LLM model
OLLAMA_MODEL = "llama3.2"

# Text splitting parameters
TEXT_SPLITTER_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
}

# Number of search results
DEFAULT_N_RESULTS = 5
```

## 🧪 Testing Components

### Document Conversion

```bash
python document_converter.py
```

### Text Chunking

```bash
python text_splitter.py
```

### Vector Store

```bash
python vector_store.py
```

### LLM Handler

```bash
python llm_handler.py
```

## 🔧 Troubleshooting

### Issue: Model not found

```bash
# Check available models
ollama list

# Download required model
ollama pull llama3.2
```

### Issue: Out of memory

- Reduce `chunk_size` in `config.py`
- Reduce `DEFAULT_N_RESULTS`
- Use a lighter model (e.g., `llama3.2:1b`)

### Issue: Slow generation

- Use a faster model
- Reduce number of search results
- Consider using GPU version of Ollama

## 📊 Performance

On Think Python document (300+ pages):

- **Conversion**: ~5 seconds
- **Indexing**: ~30 seconds (847 chunks)
- **Search**: < 1 second
- **Answer generation**: 5-15 seconds (depends on length)

## 🛣️ Roadmap

- [ ] Support more formats (Excel, PowerPoint)
- [ ] Embedding caching
- [ ] REST API endpoints
- [ ] Multimodal documents (images)
- [ ] Chat history and dialogue context
- [ ] Deploy to Hugging Face Spaces

## 📖 Sources and Inspiration

Project based on article: [How I Built a RAG System in One Evening](https://habr.com/ru/articles/955798/)

**Technologies Used:**

- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF conversion
- [LangChain](https://www.langchain.com/) - text splitting
- [ChromaDB](https://www.trychroma.com/) - vector database
- [Sentence Transformers](https://www.sbert.net/) - embeddings
- [Ollama](https://ollama.ai/) - local LLM models
- [Gradio](https://www.gradio.app/) - web interface

## 📝 License

This project is created for educational purposes. Use freely!

## 🤝 Contributing

If you want to improve the project:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Contact

If you have questions or suggestions, create an Issue in the repository.

---

**Made with ❤️ for learning RAG systems and local LLMs**
