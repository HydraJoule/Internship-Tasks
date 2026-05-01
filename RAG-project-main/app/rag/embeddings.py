import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

def get_embeddings_model():
    """
    Returns a HuggingFace embedding model to run locally without an external API.
    """
    logger.info(f"Initializing local embedding model: {settings.EMBEDDING_MODEL}")
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
