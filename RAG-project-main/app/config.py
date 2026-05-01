import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Provide a root dir reference
ROOT_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "RAG_Support_Assistant"
    
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_PROVIDER: str = "groq"
    MODEL_NAME: str = "llama-3.1-8b-instant"
    
    CHROMA_DB_DIR: str = str(ROOT_DIR / "chroma_db")
    UPLOAD_DIR: str = str(ROOT_DIR / "uploads")
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    SIMILARITY_THRESHOLD: float = 0.6
    TOP_K_RETRIEVAL: int = 8
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
