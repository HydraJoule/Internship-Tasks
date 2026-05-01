class RAGAssistantError(Exception):
    """Base exception for RAG Support Assistant."""
    pass

class DocumentIngestionError(RAGAssistantError):
    """Raised when parsing or ingesting a document fails."""
    pass

class VectorStoreError(RAGAssistantError):
    """Raised when there is an issue with the ChromaDB vector store."""
    pass

class LLMGenerationError(RAGAssistantError):
    """Raised when the LLM service fails to generate a response."""
    pass
