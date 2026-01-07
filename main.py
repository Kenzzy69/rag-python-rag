"""
Main RAG Application
Combines all components and provides a Gradio web interface
"""
import gradio as gr
import logging
from typing import Generator

from config import GRADIO_CONFIG, DEFAULT_N_RESULTS
from document_converter import download_test_document, convert_all_documents
from text_splitter import process_all_documents
from vector_store import VectorStore, retrieve_context
from llm_handler import stream_llm_answer, format_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Complete RAG (Retrieval-Augmented Generation) System
    """
    
    def __init__(self):
        """
        Initialize the RAG system
        """
        self.vector_store = None
        logger.info("RAG System initialized")
    
    def setup_pipeline(self, force_rebuild: bool = False) -> bool:
        """
        Set up the complete RAG pipeline
        
        Args:
            force_rebuild: Whether to force rebuild the vector store
            
        Returns:
            True if setup successful
        """
        try:
            # Step 1: Download test document
            logger.info("Step 1: Downloading test document...")
            test_doc = download_test_document()
            if not test_doc:
                logger.error("Failed to download test document")
                return False
            
            # Step 2: Convert documents to markdown
            logger.info("Step 2: Converting documents to markdown...")
            converted = convert_all_documents()
            if not converted:
                logger.error("No documents were converted")
                return False
            logger.info(f"Converted {len(converted)} documents")
            
            # Step 3: Split documents into chunks
            logger.info("Step 3: Splitting documents into chunks...")
            chunks = process_all_documents()
            if not chunks:
                logger.error("No chunks were created")
                return False
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 4: Initialize vector store
            logger.info("Step 4: Initializing vector store...")
            self.vector_store = VectorStore()
            
            # Check if vector store is empty or force rebuild
            stats = self.vector_store.get_collection_stats()
            if stats["document_count"] == 0 or force_rebuild:
                if force_rebuild and stats["document_count"] > 0:
                    logger.info("Clearing existing vector store...")
                    self.vector_store.clear_collection()
                
                logger.info("Adding documents to vector store...")
                self.vector_store.add_documents(chunks)
            else:
                logger.info(f"Vector store already contains {stats['document_count']} documents")
            
            logger.info("✅ RAG pipeline setup complete!")
            return True
        
        except Exception as e:
            logger.error(f"Error setting up pipeline: {e}")
            return False
    
    def query(
        self,
        question: str,
        n_results: int = DEFAULT_N_RESULTS
    ) -> Generator[str, None, None]:
        """
        Process a query and stream the response
        
        Args:
            question: User's question
            n_results: Number of context chunks to retrieve
            
        Yields:
            Response text parts
        """
        if not question.strip():
            yield "❌ Please enter a question."
            return
        
        try:
            # Retrieve context
            logger.info(f"Processing query: {question}")
            context, sources = retrieve_context(question, n_results)
            
            if not context:
                yield "❌ No relevant information found in the documents."
                return
            
            # Start response
            response_start = f"**Question:** {question}\n\n**Answer:** "
            answer = ""
            
            # Stream the answer
            for token in stream_llm_answer(question, context):
                answer += token
                yield response_start + answer
            
            # Add sources at the end
            final_response = format_response(question, answer, sources)
            yield final_response
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            yield f"❌ Error: {str(e)}"


# Global RAG system instance
rag_system = RAGSystem()


def rag_interface(question: str) -> Generator[str, None, None]:
    """
    Gradio interface function
    
    Args:
        question: User's question
        
    Yields:
        Response text parts
    """
    yield from rag_system.query(question)


def create_gradio_interface() -> gr.Interface:
    """
    Create the Gradio web interface
    
    Returns:
        Gradio Interface object
    """
    interface = gr.Interface(
        fn=rag_interface,
        inputs=gr.Textbox(
            label="Your Question",
            placeholder="Ask anything about Python programming...",
            lines=3
        ),
        outputs=gr.Markdown(label="Answer"),
        title=GRADIO_CONFIG["title"],
        description=GRADIO_CONFIG["description"],
        examples=GRADIO_CONFIG["examples"],
        theme=GRADIO_CONFIG["theme"],
        allow_flagging="never"
    )
    
    return interface


def main():
    """
    Main entry point for the application
    """
    logger.info("🚀 Starting RAG System...")
    
    # Setup the pipeline
    logger.info("Setting up RAG pipeline...")
    success = rag_system.setup_pipeline(force_rebuild=False)
    
    if not success:
        logger.error("Failed to setup RAG pipeline. Please check the logs.")
        return
    
    # Create and launch Gradio interface
    logger.info("Creating Gradio interface...")
    interface = create_gradio_interface()
    
    logger.info("Launching web interface...")
    interface.queue().launch(
        share=GRADIO_CONFIG["share"],
        server_name="0.0.0.0",
        server_port=7860,
    )


if __name__ == "__main__":
    main()
