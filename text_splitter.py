"""
Text Splitting Module
Splits documents into chunks for embedding and retrieval
"""
from pathlib import Path
from typing import List, Dict
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    PROCESSED_DOCS_DIR,
    TEXT_SPLITTER_CONFIG,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Handles document chunking with configurable parameters
    """
    
    def __init__(
        self,
        chunk_size: int = TEXT_SPLITTER_CONFIG["chunk_size"],
        chunk_overlap: int = TEXT_SPLITTER_CONFIG["chunk_overlap"],
        separators: List[str] = TEXT_SPLITTER_CONFIG["separators"],
        keep_separator: bool = TEXT_SPLITTER_CONFIG["keep_separator"],
    ):
        """
        Initialize the document chunker
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separator strings to split on
            keep_separator: Whether to keep the separator in the chunks
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            keep_separator=keep_separator,
        )
        logger.info(
            f"Initialized text splitter: chunk_size={chunk_size}, "
            f"chunk_overlap={chunk_overlap}"
        )
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks
        """
        try:
            chunks = self.splitter.split_text(text)
            logger.debug(f"Split text into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            raise
    
    def split_document(self, file_path: Path) -> List[Dict[str, str]]:
        """
        Split a markdown document into chunks with metadata
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of dictionaries containing chunk text and metadata
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Split into chunks
            chunks = self.split_text(text)
            
            # Add metadata to each chunk
            chunk_data = []
            for idx, chunk in enumerate(chunks):
                chunk_data.append({
                    "text": chunk,
                    "source": file_path.name,
                    "chunk_id": idx,
                    "total_chunks": len(chunks),
                })
            
            logger.info(f"Split {file_path.name} into {len(chunks)} chunks")
            return chunk_data
        
        except Exception as e:
            logger.error(f"Error splitting document {file_path}: {e}")
            raise


def process_all_documents() -> List[Dict[str, str]]:
    """
    Process all markdown documents in the processed_docs directory
    
    Returns:
        List of all chunks with metadata from all documents
    """
    chunker = DocumentChunker()
    all_chunks = []
    
    if not PROCESSED_DOCS_DIR.exists():
        logger.error(f"Processed documents directory not found: {PROCESSED_DOCS_DIR}")
        return all_chunks
    
    # Process all markdown files
    markdown_files = list(PROCESSED_DOCS_DIR.glob("*.md"))
    
    if not markdown_files:
        logger.warning("No markdown files found in processed_docs directory")
        return all_chunks
    
    logger.info(f"Processing {len(markdown_files)} documents...")
    
    for file_path in markdown_files:
        try:
            chunks = chunker.split_document(file_path)
            all_chunks.extend(chunks)
            logger.info(f"Added {len(chunks)} chunks from {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            continue
    
    logger.info(f"Total chunks processed: {len(all_chunks)}")
    return all_chunks


def get_chunk_statistics(chunks: List[Dict[str, str]]) -> Dict:
    """
    Calculate statistics about the chunks
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Dictionary with statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_characters": 0,
            "avg_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
            "sources": [],
        }
    
    chunk_sizes = [len(chunk["text"]) for chunk in chunks]
    sources = list(set(chunk["source"] for chunk in chunks))
    
    return {
        "total_chunks": len(chunks),
        "total_characters": sum(chunk_sizes),
        "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
        "min_chunk_size": min(chunk_sizes),
        "max_chunk_size": max(chunk_sizes),
        "sources": sources,
        "num_sources": len(sources),
    }


if __name__ == "__main__":
    # Test the text splitting
    logger.info("Testing text splitting...")
    
    chunks = process_all_documents()
    
    if chunks:
        stats = get_chunk_statistics(chunks)
        logger.info(f"Chunk statistics: {stats}")
        
        # Display first chunk as example
        if chunks:
            logger.info("\nExample chunk:")
            logger.info(f"Source: {chunks[0]['source']}")
            logger.info(f"Chunk ID: {chunks[0]['chunk_id']}")
            logger.info(f"Text preview: {chunks[0]['text'][:200]}...")
    else:
        logger.warning("No chunks created. Make sure documents are converted first.")
