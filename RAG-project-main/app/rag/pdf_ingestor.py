import os
from pypdf import PdfReader
from typing import List, Dict, Any
from app.utils.logger import get_logger
from app.utils.exceptions import DocumentIngestionError

logger = get_logger(__name__)

class PDFIngestor:
    @staticmethod
    def process_pdf(file_path: str, session_id: str, original_filename: str) -> List[Dict[str, Any]]:
        """
        Reads a PDF file and extracts text page by page.
        Returns a list of dicts with text and metadata.
        """
        logger.info(f"Processing PDF: {file_path} for session {session_id}")
        pages_data = []
        try:
            reader = PdfReader(file_path)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text = text.strip()
                if text:
                    metadata = {
                        "source": original_filename,
                        "page": page_num + 1,
                        "session_id": session_id
                    }
                    pages_data.append({"text": text, "metadata": metadata})
            logger.info(f"Extracted {len(pages_data)} pages from {original_filename}.")
            return pages_data
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            raise DocumentIngestionError(f"Failed to extract text from {original_filename}: {str(e)}")
