"""
Vector store implementation for the RAG system.
Handles storage and retrieval of embeddings for semantic search.
"""
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pickle
import os
import hashlib
from ..utils.logger import get_logger


@dataclass
class Document:
    """Represents a document in the vector store"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class VectorStore:
    """Vector store for storing and retrieving embeddings"""
    
    def __init__(self, storage_path: str = "./vector_store.pkl"):
        self.storage_path = storage_path
        self.documents: Dict[str, Document] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.document_ids: List[str] = []
        self._lock = asyncio.Lock()
        self._logger = get_logger(__name__)
        
        # Load existing data if available
        self.load()
    
    async def add_document(self, doc: Document) -> bool:
        """Add a document to the vector store"""
        async with self._lock:
            try:
                self.documents[doc.id] = doc
                self.document_ids.append(doc.id)

                # Update embeddings matrix if embedding is provided
                if doc.embedding is not None:
                    self._update_embeddings_matrix()

                self._logger.info(f"Added document {doc.id} to vector store")
                return True
            except Exception as e:
                self._logger.error(f"Error adding document {doc.id}: {e}")
                return False
    
    def add_documents(self, docs: List[Document]) -> List[bool]:
        """Add multiple documents to the vector store"""
        results = []
        for doc in docs:
            results.append(self.add_document(doc))
        return results
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the vector store"""
        with self._lock:
            if doc_id in self.documents:
                del self.documents[doc_id]
                if doc_id in self.document_ids:
                    self.document_ids.remove(doc_id)
                self._update_embeddings_matrix()
                self._logger.info(f"Removed document {doc_id} from vector store")
                return True
            return False
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.documents.get(doc_id)
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents using cosine similarity"""
        if self.embeddings_matrix is None or len(self.embeddings_matrix) == 0:
            return []
            
        # Calculate cosine similarity
        similarities = self._cosine_similarity(query_embedding, self.embeddings_matrix)
        
        # Get top-k most similar documents
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.document_ids):
                doc_id = self.document_ids[idx]
                if doc_id in self.documents:
                    doc = self.documents[doc_id]
                    similarity = float(similarities[idx])
                    results.append((doc, similarity))
        
        return results
    
    def _cosine_similarity(self, query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and embeddings"""
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Normalize vectors
        query_norm = query / np.linalg.norm(query)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Calculate dot product (cosine similarity)
        similarities = np.dot(embeddings_norm, query_norm)
        
        return similarities
    
    def _update_embeddings_matrix(self):
        """Update the embeddings matrix from stored documents"""
        embeddings_list = []
        valid_doc_ids = []
        
        for doc_id in self.document_ids:
            if doc_id in self.documents and self.documents[doc_id].embedding is not None:
                embeddings_list.append(self.documents[doc_id].embedding)
                valid_doc_ids.append(doc_id)
        
        if embeddings_list:
            self.embeddings_matrix = np.array(embeddings_list)
            self.document_ids = valid_doc_ids
        else:
            self.embeddings_matrix = None
            self.document_ids = []
    
    def save(self):
        """Save the vector store to disk"""
        try:
            data = {
                'documents': self.documents,
                'document_ids': self.document_ids
            }
            
            with open(self.storage_path, 'wb') as f:
                pickle.dump(data, f)
                
            self._logger.info(f"Vector store saved to {self.storage_path}")
        except Exception as e:
            self._logger.error(f"Error saving vector store: {e}")
    
    def load(self):
        """Load the vector store from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'rb') as f:
                    data = pickle.load(f)
                
                self.documents = data.get('documents', {})
                self.document_ids = data.get('document_ids', [])
                self._update_embeddings_matrix()
                
                self._logger.info(f"Vector store loaded from {self.storage_path}")
            except Exception as e:
                self._logger.error(f"Error loading vector store: {e}")
    
    def clear(self):
        """Clear all documents from the vector store"""
        with self._lock:
            self.documents = {}
            self.document_ids = []
            self.embeddings_matrix = None
            self._logger.info("Vector store cleared")


# Global vector store instance
vector_store = VectorStore()


def get_vector_store() -> VectorStore:
    """Get the global vector store instance"""
    return vector_store