"""
Embedding service for the RAG system.
Handles generation of embeddings for documents and queries.
"""
import numpy as np
from typing import List, Union
import hashlib
from ..utils.logger import get_logger


class EmbeddingService:
    """Service for generating embeddings using transformer models"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._logger = get_logger(__name__)
        self._load_model()

    def _load_model(self):
        """Load the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self._logger.info(f"Loaded embedding model: {self.model_name}")
        except ImportError:
            self._logger.warning("sentence_transformers not available, using fallback embedding")
            self.model = None
        except Exception as e:
            self._logger.error(f"Failed to load embedding model {self.model_name}: {e}")
            self.model = None
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        if self.model:
            try:
                embedding = self.model.encode([text])[0]
                return embedding.astype(np.float32)
            except Exception as e:
                self._logger.error(f"Error generating embedding: {e}")
        
        # Fallback: simple hash-based embedding for demo purposes
        return self._hash_based_embedding(text)
    
    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        if self.model:
            try:
                embeddings = self.model.encode(texts)
                return [emb.astype(np.float32) for emb in embeddings]
            except Exception as e:
                self._logger.error(f"Error generating embeddings: {e}")
        
        # Fallback: simple hash-based embeddings for demo purposes
        return [self._hash_based_embedding(text) for text in texts]
    
    def _hash_based_embedding(self, text: str) -> np.ndarray:
        """Fallback embedding using hash functions (for demo purposes)"""
        # Create a simple hash-based embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hex to float array
        embedding = np.zeros(384, dtype=np.float32)  # Match typical embedding size
        
        for i, char in enumerate(text_hash):
            if i < len(embedding):
                embedding[i] = ord(char) / 255.0  # Normalize to 0-1 range
        
        return embedding


# Global embedding service instance
embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    return embedding_service