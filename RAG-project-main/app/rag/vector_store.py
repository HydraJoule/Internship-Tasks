import chromadb
from typing import List, Dict, Any
from app.config import settings
from app.rag.embeddings import get_embeddings_model
from app.utils.logger import get_logger

logger = get_logger(__name__)

class VectorStoreManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        self.embedding_model = get_embeddings_model()
    
    def _get_embedding_fn(self):
        class SimpleEmbedding:
            def __init__(self, model):
                self.model = model
            def __call__(self, input):
                # Ensure input is a list of strings
                if isinstance(input, str):
                    input = [input]
                elif not isinstance(input, list):
                    input = list(input)
                return self.model.embed_documents(input)
            def embed_query(self, input):
                if isinstance(input, str):
                    return self.model.embed_query(input)
                elif isinstance(input, list) and len(input) > 0:
                    return [self.model.embed_query(q) for q in input]
                return []
            def name(self):
                return "langchain_embedding_custom_model"
        return SimpleEmbedding(self.embedding_model)

    def ingest_chunks(self, session_id: str, chunks: List[Dict[str, Any]]):
        """
        Creates a collection for a session (if not exists) and adds chunks.
        """
        logger.info(f"Ingesting {len(chunks)} chunks into vector store for session: {session_id}")
        
        # Collection names must be strictly alphanumeric/underscores without dots.
        clean_session_id = session_id.replace("-", "_").replace(".", "_")
        collection_name = f"session_{clean_session_id}"
        
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name, 
                embedding_function=self._get_embedding_fn()
            )
            
            ids = [f"{c['metadata']['source']}_p{c['metadata']['page']}_c{c['metadata']['chunk_id']}" for c in chunks]
            texts = [c["text"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            
            collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            logger.info("Successfully ingested chunks into ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to ingest chunks: {e}")
            raise

    def query(self, session_id: str, query: str, top_k: int = settings.TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        clean_session_id = session_id.replace("-", "_").replace(".", "_")
        collection_name = f"session_{clean_session_id}"
        try:
            collection = self.client.get_collection(name=collection_name, embedding_function=self._get_embedding_fn())
            
            results = collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            if not results["documents"] or len(results["documents"]) == 0 or len(results["documents"][0]) == 0:
                return []
                
            docs, metas = results["documents"][0], results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0]*len(docs)
            
            retrieved = []
            for doc, meta, d in zip(docs, metas, distances):
                retrieved.append({
                    "text": doc,
                    "metadata": meta,
                    "score": 1 - d if d else 0 # Approximate
                })
            return retrieved
        except Exception as e:
            import traceback
            logger.error(f"Collection {collection_name} not found or query failed: {e}\n{traceback.format_exc()}")
            return []
            
    def clear_session(self, session_id: str):
        clean_session_id = session_id.replace("-", "_").replace(".", "_")
        collection_name = f"session_{clean_session_id}"
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Cleared ChromaDB collection: {collection_name}")
        except Exception:
            pass # Collection does not exist
