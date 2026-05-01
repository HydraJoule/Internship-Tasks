from typing import List, Dict, Any
from app.rag.vector_store import VectorStoreManager
from app.config import settings

class ContextRetriever:
    def __init__(self):
        self.vector_store = VectorStoreManager()
    
    def retrieve_for_session(self, session_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves top k chunks based on user query within a specific session.
        """
        results = self.vector_store.query(session_id, query, top_k=settings.TOP_K_RETRIEVAL)
        return results
