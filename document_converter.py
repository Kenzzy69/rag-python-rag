"""
Document Conversion Module
Converts various document formats (PDF, DOCX, TXT) to markdown format
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional
import logging
from docx import Document

from config import (
    DOCUMENTS_DIR,
    PROCESSED_DOCS_DIR,
    SUPPORTED_FORMATS,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_pdf_to_markdown(pdf_path: Path) -> str:
    """
    Convert PDF file to markdown format using PyMuPDF
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Markdown formatted text
    """
    try:
        doc = fitz.open(pdf_path)
        markdown_content = []
        
        for page_num, page in enumerate(doc, 1):
            # Extract text from page
            text = page.get_text()
            
            # Add page header
            markdown_content.append(f"\n## Page {page_num}\n")
            markdown_content.append(text)
        
        doc.close()
        return "\n".join(markdown_content)
    
    except Exception as e:
        logger.error(f"Error converting PDF {pdf_path}: {e}")
        raise


def convert_docx_to_markdown(docx_path: Path) -> str:
    """
    Convert DOCX file to markdown format
    
    Args:
        docx_path: Path to the DOCX file
        
    Returns:
        Markdown formatted text
    """
    try:
        doc = Document(docx_path)
        markdown_content = []
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # Determine heading level based on style
            if para.style.name.startswith('Heading'):
                level = para.style.name.replace('Heading ', '')
                if level.isdigit():
                    markdown_content.append(f"\n{'#' * int(level)} {text}\n")
                else:
                    markdown_content.append(f"\n## {text}\n")
            else:
                markdown_content.append(text)
        
        return "\n".join(markdown_content)
    
    except Exception as e:
        logger.error(f"Error converting DOCX {docx_path}: {e}")
        raise


def convert_txt_to_markdown(txt_path: Path) -> str:
    """
    Read plain text file (already in markdown or plain text format)
    
    Args:
        txt_path: Path to the text file
        
    Returns:
        File content as string
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(txt_path, 'r', encoding='latin-1') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading text file {txt_path}: {e}")
        raise


def convert_document_to_markdown(file_path: Path) -> Optional[str]:
    """
    Convert a document to markdown format based on its extension
    
    Args:
        file_path: Path to the document
        
    Returns:
        Markdown formatted text or None if conversion fails
    """
    suffix = file_path.suffix.lower()
    
    if suffix not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported format: {suffix}")
        return None
    
    try:
        if suffix == '.pdf':
            return convert_pdf_to_markdown(file_path)
        elif suffix == '.docx':
            return convert_docx_to_markdown(file_path)
        elif suffix in ['.txt', '.md']:
            return convert_txt_to_markdown(file_path)
        else:
            logger.warning(f"No converter available for {suffix}")
            return None
    
    except Exception as e:
        logger.error(f"Failed to convert {file_path}: {e}")
        return None


def convert_all_documents() -> dict[str, Path]:
    """
    Convert all documents in the documents directory to markdown
    
    Returns:
        Dictionary mapping original filenames to converted file paths
    """
    converted_files = {}
    
    if not DOCUMENTS_DIR.exists():
        logger.error(f"Documents directory not found: {DOCUMENTS_DIR}")
        return converted_files
    
    # Find all supported documents
    for file_path in DOCUMENTS_DIR.iterdir():
        if file_path.suffix.lower() not in SUPPORTED_FORMATS:
            continue
        
        if file_path.name.startswith('.'):
            continue
        
        logger.info(f"Converting {file_path.name}...")
        
        # Convert to markdown
        markdown_content = convert_document_to_markdown(file_path)
        
        if markdown_content is None:
            logger.warning(f"Skipping {file_path.name}")
            continue
        
        # Save converted content
        output_filename = file_path.stem + ".md"
        output_path = PROCESSED_DOCS_DIR / output_filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            converted_files[file_path.name] = output_path
            logger.info(f"Successfully converted {file_path.name} -> {output_filename}")
        
        except Exception as e:
            logger.error(f"Failed to save {output_filename}: {e}")
    
    logger.info(f"Converted {len(converted_files)} documents")
    return converted_files


def download_test_document() -> Optional[Path]:
    """
    Download the test document (Think Python PDF) if not already present
    
    Returns:
        Path to the downloaded file or None if download fails
    """
    import requests
    from config import TEST_DOCUMENT_URL, TEST_DOCUMENT_NAME
    
    output_path = DOCUMENTS_DIR / TEST_DOCUMENT_NAME
    
    if output_path.exists():
        logger.info(f"Test document already exists: {TEST_DOCUMENT_NAME}")
        return output_path
    
    try:
        logger.info(f"Downloading test document from {TEST_DOCUMENT_URL}...")
        response = requests.get(TEST_DOCUMENT_URL, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Successfully downloaded {TEST_DOCUMENT_NAME}")
        return output_path
    
    except Exception as e:
        logger.error(f"Failed to download test document: {e}")
        return None


if __name__ == "__main__":
    # Test the conversion functions
    logger.info("Testing document conversion...")
    
    # Download test document
    test_doc = download_test_document()
    
    if test_doc:
        # Convert all documents
        converted = convert_all_documents()
        logger.info(f"Conversion complete. Converted files: {list(converted.keys())}")
    else:
        logger.error("Failed to download test document")
