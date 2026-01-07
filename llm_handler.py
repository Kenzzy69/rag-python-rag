"""
LLM Handler Module
Manages interaction with Ollama LLM for answer generation
"""
import ollama
from typing import Generator, Dict, List
import logging

from config import (
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    SYSTEM_PROMPT,
    PROMPT_TEMPLATE,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMHandler:
    """
    Handles LLM interactions using Ollama
    """
    
    def __init__(self, model: str = OLLAMA_MODEL):
        """
        Initialize the LLM handler
        
        Args:
            model: Name of the Ollama model to use
        """
        self.model = model
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
        logger.info(f"Initialized LLM handler with model: {model}")
        
        # Verify model is available
        try:
            self.verify_model()
        except Exception as e:
            logger.error(f"Failed to verify model: {e}")
            raise
    
    def verify_model(self) -> bool:
        """
        Verify that the model is available in Ollama
        
        Returns:
            True if model is available
        """
        try:
            models = self.client.list()
            available_models = [m.model for m in models.models]
            
            # Check if model name matches any available model
            model_available = any(
                self.model in model_name
                for model_name in available_models
            )
            
            if model_available:
                logger.info(f"Model {self.model} is available")
                return True
            else:
                logger.error(
                    f"Model {self.model} not found. "
                    f"Available models: {available_models}"
                )
                return False
        except Exception as e:
            logger.error(f"Error verifying model: {e}")
            raise
    
    def generate_answer(
        self,
        question: str,
        context: str,
        stream: bool = False
    ) -> str:
        """
        Generate an answer based on the question and context
        
        Args:
            question: User's question
            context: Retrieved context from documents
            stream: Whether to stream the response
            
        Returns:
            Generated answer
        """
        # Format the prompt
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                system=SYSTEM_PROMPT,
                stream=stream,
            )
            
            if not stream:
                return response['response']
            else:
                return response
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def stream_answer(
        self,
        question: str,
        context: str
    ) -> Generator[str, None, None]:
        """
        Stream the answer generation token by token
        
        Args:
            question: User's question
            context: Retrieved context from documents
            
        Yields:
            Generated text tokens
        """
        # Format the prompt
        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        try:
            stream = self.client.generate(
                model=self.model,
                prompt=prompt,
                system=SYSTEM_PROMPT,
                stream=True,
            )
            
            for chunk in stream:
                if 'response' in chunk:
                    yield chunk['response']
        
        except Exception as e:
            logger.error(f"Error streaming answer: {e}")
            raise


def format_response(
    question: str,
    answer: str,
    sources: List[Dict]
) -> str:
    """
    Format the final response with question, answer, and sources
    
    Args:
        question: User's question
        answer: Generated answer
        sources: List of source documents
        
    Returns:
        Formatted response in markdown
    """
    # Create response header
    response_parts = [
        f"**Question:** {question}\n",
        f"**Answer:** {answer}\n",
    ]
    
    # Add sources section
    if sources:
        response_parts.append("\n**Sources:**\n")
        
        # Group sources by document
        sources_by_doc = {}
        for source in sources:
            doc_name = source["source"]
            if doc_name not in sources_by_doc:
                sources_by_doc[doc_name] = []
            sources_by_doc[doc_name].append(source)
        
        # Format sources
        for doc_name, doc_sources in sources_by_doc.items():
            chunks = ", ".join([s["chunk_id"] for s in doc_sources])
            avg_similarity = sum(s["similarity"] for s in doc_sources) / len(doc_sources)
            response_parts.append(
                f"- {doc_name} (chunks: {chunks}, "
                f"relevance: {avg_similarity:.2%})\n"
            )
    
    return "".join(response_parts)


def stream_llm_answer(
    question: str,
    context: str
) -> Generator[str, None, None]:
    """
    Stream answer generation for a question with context
    
    Args:
        question: User's question
        context: Retrieved context
        
    Yields:
        Generated text tokens
    """
    llm = LLMHandler()
    
    try:
        for token in llm.stream_answer(question, context):
            yield token
    except Exception as e:
        logger.error(f"Error in stream_llm_answer: {e}")
        yield f"\n\n❌ Error generating answer: {str(e)}"


def generate_answer(
    question: str,
    context: str
) -> str:
    """
    Generate a complete answer for a question with context
    
    Args:
        question: User's question
        context: Retrieved context
        
    Returns:
        Generated answer
    """
    llm = LLMHandler()
    
    try:
        answer = llm.generate_answer(question, context, stream=False)
        return answer
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return f"❌ Error generating answer: {str(e)}"


if __name__ == "__main__":
    # Test the LLM handler
    logger.info("Testing LLM handler...")
    
    # Create LLM instance
    llm = LLMHandler()
    
    # Test answer generation
    test_question = "What is Python?"
    test_context = "Python is a high-level programming language known for its simplicity and readability."
    
    logger.info(f"\nTest Question: {test_question}")
    logger.info(f"Context: {test_context}\n")
    
    # Test streaming
    logger.info("Streaming answer:")
    for token in llm.stream_answer(test_question, test_context):
        print(token, end='', flush=True)
    print("\n")
    
    # Test non-streaming
    logger.info("\nGenerating complete answer:")
    answer = llm.generate_answer(test_question, test_context)
    logger.info(f"Answer: {answer}")
