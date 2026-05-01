from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

class TextChunker:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes raw page text and splits it into chunks, preserving metadata.
        """
        chunked_data = []
        for doc in documents:
            chunks = self.text_splitter.split_text(doc["text"])
            for idx, chunk_text in enumerate(chunks):
                # We do a deep copy of metadata so each chunk has its own block
                chunk_meta = doc["metadata"].copy()
                chunk_meta["chunk_id"] = idx
                chunked_data.append({
                    "text": chunk_text,
                    "metadata": chunk_meta
                })
        return chunked_data
