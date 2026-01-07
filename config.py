"""
Configuration file for RAG System
Contains all settings and parameters for the document processing pipeline
"""
from pathlib import Path
from typing import List

# Project Paths
PROJECT_ROOT = Path(__file__).parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
PROCESSED_DOCS_DIR = PROJECT_ROOT / "processed_docs"
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

# Ensure directories exist
DOCUMENTS_DIR.mkdir(exist_ok=True)
PROCESSED_DOCS_DIR.mkdir(exist_ok=True)
CHROMA_DB_DIR.mkdir(exist_ok=True)

# Document Processing Settings
SUPPORTED_FORMATS = [".pdf", ".docx", ".txt", ".md"]

# Text Splitting Configuration
TEXT_SPLITTER_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "separators": ["\n\n", "\n", ". ", " ", ""],
    "keep_separator": True,
}

# Embedding Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Vector Database Configuration
CHROMA_COLLECTION_NAME = "document_embeddings"
CHROMA_DISTANCE_METRIC = "cosine"

# LLM Configuration
OLLAMA_MODEL = "llama3.2"
OLLAMA_BASE_URL = "http://localhost:11434"

# Retrieval Configuration
DEFAULT_N_RESULTS = 5
SIMILARITY_THRESHOLD = 0.5

# Prompt Templates
SYSTEM_PROMPT = """You are a helpful assistant. Answer the question based on the context provided.
Be concise and accurate. If you don't know the answer based on the context, say so."""

PROMPT_TEMPLATE = """Context: {context}

Question: {question}

Answer:"""

# Gradio Interface Configuration
GRADIO_CONFIG = {
    "title": "Intelligent Document Q&A System",
    "description": "Ask questions about your documents and get instant answers with source citations.",
    "examples": [
        "How do if-else statements work in Python?",
        "What are the different types of loops in Python?",
        "How do you handle errors in Python?",
        "Explain Python functions with examples",
        "What is object-oriented programming in Python?",
    ],
    "theme": "default",
    "share": False,  # Set to True to create a public link
}

# Test Document URL (Think Python book)
TEST_DOCUMENT_URL = "https://greenteapress.com/thinkpython/thinkpython.pdf"
TEST_DOCUMENT_NAME = "think_python_guide.pdf"
