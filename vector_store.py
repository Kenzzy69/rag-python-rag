"""
Vector Store Module
Handles embedding generation and ChromaDB vector storage
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import logging

from config import (
    CHROMA_DB_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages vector embeddings and ChromaDB storage
    """
    
    def __init__(self):
        """
        Initialize the vector store with embedding model and ChromaDB client
        """
        # Initialize embedding model
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at: {CHROMA_DB_DIR}")
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Collection '{CHROMA_COLLECTION_NAME}' ready")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, str]]) -> None:
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        logger.info(f"Adding {len(chunks)} chunks to vector store...")
        
        # Extract texts and metadata
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "source": chunk["source"],
                "chunk_id": str(chunk["chunk_id"]),
                "total_chunks": str(chunk["total_chunks"]),
            }
            for chunk in chunks
        ]
        
        # Generate unique IDs for each chunk
        ids = [
            f"{chunk['source']}_chunk_{chunk['chunk_id']}"
            for chunk in chunks
        ]
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.generate_embeddings(texts)
        
        # Add to ChromaDB
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5
    ) -> Tuple[List[str], List[Dict], List[float]]:
        """
        Search for similar documents
        
        Args:
            query: Query text
            n_results: Number of results to return
            
        Returns:
            Tuple of (documents, metadatas, distances)
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )
            
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            distances = results["distances"][0] if results["distances"] else []
            
            logger.info(f"Found {len(documents)} results for query")
            return documents, metadatas, distances
        
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "collection_name": CHROMA_COLLECTION_NAME,
            "document_count": count,
            "embedding_model": EMBEDDING_MODEL,
        }
    
    def clear_collection(self) -> None:
        """
        Clear all documents from the collection
        """
        try:
            self.client.delete_collection(name=CHROMA_COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise


def retrieve_context(
    query: str,
    n_results: int = 5
) -> Tuple[str, List[Dict]]:
    """
    Retrieve context for a query from the vector store
    
    Args:
        query: User query
        n_results: Number of results to retrieve
        
    Returns:
        Tuple of (context string, list of source documents)
    """
    vector_store = VectorStore()
    
    # Search for relevant documents
    documents, metadatas, distances = vector_store.search(query, n_results)
    
    if not documents:
        logger.warning("No relevant documents found")
        return "", []
    
    # Combine documents into context
    context_parts = []
    source_docs = []
    
    for doc, metadata, distance in zip(documents, metadatas, distances):
        context_parts.append(doc)
        source_docs.append({
            "source": metadata.get("source", "Unknown"),
            "chunk_id": metadata.get("chunk_id", "0"),
            "similarity": 1 - distance,  # Convert distance to similarity
        })
    
    context = "\n\n---\n\n".join(context_parts)
    
    logger.info(f"Retrieved context from {len(documents)} chunks")
    return context, source_docs


if __name__ == "__main__":
    # Test the vector store
    logger.info("Testing vector store...")
    
    # Create vector store instance
    vs = VectorStore()
    
    # Get statistics
    stats = vs.get_collection_stats()
    logger.info(f"Collection stats: {stats}")
    
    # Test search if collection is not empty
    if stats["document_count"] > 0:
        test_query = "How do loops work in Python?"
        logger.info(f"\nTesting search with query: '{test_query}'")
        context, sources = retrieve_context(test_query, n_results=3)
        
        logger.info(f"\nRetrieved context ({len(context)} chars)")
        logger.info(f"Sources: {sources}")
    else:
        logger.info("Collection is empty. Run document processing first.")
