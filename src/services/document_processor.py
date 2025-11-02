"""Document processing service for PDF/OCR extraction."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
import pdfplumber
from PIL import Image
import io

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available. OCR functionality will be limited.")

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process financial documents (PDF, images, etc.)."""
    
    def __init__(self):
        self.supported_formats = [".pdf", ".png", ".jpg", ".jpeg", ".docx"]
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def process_document(self, file_path: Path, file_content: bytes = None) -> Dict[str, Any]:
        """Process a document and extract text/data.
        
        Args:
            file_path: Path to the document
            file_content: Optional file content as bytes
        
        Returns:
            Dictionary with extracted text, metadata, and chunks
        """
        logger.info(f"Processing document: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == ".pdf":
            return await self._process_pdf(file_path, file_content)
        elif file_extension in [".png", ".jpg", ".jpeg"]:
            return await self._process_image(file_path, file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def _process_pdf(self, file_path: Path, file_content: bytes = None) -> Dict[str, Any]:
        """Extract text from PDF."""
        text_content = []
        metadata = {"file_type": "pdf"}
        
        try:
            # Try pdfplumber first (better for tables)
            if file_content:
                pdf_file = io.BytesIO(file_content)
            else:
                pdf_file = str(file_path)
            
            with pdfplumber.open(pdf_file) as pdf:
                metadata["pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"[Page {page_num}]\n{text}")
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    if tables:
                        metadata[f"tables_page_{page_num}"] = len(tables)
        
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                if file_content:
                    pdf_file = io.BytesIO(file_content)
                else:
                    pdf_file = open(file_path, "rb")
                
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                metadata["pages"] = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"[Page {page_num}]\n{text}")
                
                if not file_content:
                    pdf_file.close()
            
            except Exception as e2:
                logger.error(f"PyPDF2 also failed: {e2}")
                raise
        
        full_text = "\n\n".join(text_content)
        
        return {
            "text": full_text,
            "metadata": metadata,
            "chunks": self._chunk_text(full_text),
            "word_count": len(full_text.split())
        }
    
    async def _process_image(self, file_path: Path, file_content: bytes = None) -> Dict[str, Any]:
        """Extract text from image using OCR."""
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("Tesseract OCR is not available. Install pytesseract and tesseract-ocr.")
        
        try:
            if file_content:
                image = Image.open(io.BytesIO(file_content))
            else:
                image = Image.open(file_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            metadata = {
                "file_type": "image",
                "format": image.format,
                "size": image.size,
                "mode": image.mode
            }
            
            return {
                "text": text,
                "metadata": metadata,
                "chunks": self._chunk_text(text),
                "word_count": len(text.split())
            }
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                    end = start + break_point + 1
                    chunk_text = text[start:end]
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text.strip(),
                "start_char": start,
                "end_char": end,
                "length": len(chunk_text)
            })
            
            start = end - overlap
            chunk_id += 1
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities like amounts, dates, etc.
        
        Args:
            text: Text to extract entities from
        
        Returns:
            Dictionary of entity types and their values
        """
        import re
        
        entities = {
            "amounts": [],
            "dates": [],
            "account_numbers": []
        }
        
        # Extract currency amounts (e.g., $1,234.56)
        amount_pattern = r'\$[\d,]+\.?\d*'
        entities["amounts"] = re.findall(amount_pattern, text)
        
        # Extract dates (simple patterns)
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}'
        ]
        for pattern in date_patterns:
            entities["dates"].extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract account numbers (simple pattern)
        account_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        entities["account_numbers"] = re.findall(account_pattern, text)
        
        return entities