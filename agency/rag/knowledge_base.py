"""
Knowledge base implementation for the RAG system.
Manages storage and retrieval of knowledge documents.
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from .vector_store import VectorStore, Document, get_vector_store
from .embeddings import EmbeddingService, get_embedding_service
from ..utils.logger import get_logger


class KnowledgeBase:
    """Knowledge base for storing and retrieving information"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.embedding_service = get_embedding_service()
        self._logger = get_logger(__name__)
    
    async def add_document(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> bool:
        """Add a document to the knowledge base"""
        try:
            # Generate embedding for the content
            embedding = self.embedding_service.embed_text(content)
            
            # Create document ID if not provided
            if doc_id is None:
                import hashlib
                doc_id = hashlib.md5((content + str(datetime.now())).encode()).hexdigest()
            
            # Create document object
            doc = Document(
                id=doc_id,
                content=content,
                metadata=metadata or {},
                embedding=embedding
            )
            
            # Add to vector store
            result = await self.vector_store.add_document(doc)
            
            if result:
                self._logger.info(f"Added document {doc_id} to knowledge base")
            else:
                self._logger.error(f"Failed to add document {doc_id} to knowledge base")
            
            return result
        except Exception as e:
            self._logger.error(f"Error adding document to knowledge base: {e}")
            return False
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> List[bool]:
        """Add multiple documents to the knowledge base"""
        results = []
        for doc_data in documents:
            content = doc_data.get("content", "")
            metadata = doc_data.get("metadata", {})
            doc_id = doc_data.get("id")
            
            result = await self.add_document(content, metadata, doc_id)
            results.append(result)
        
        return results
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.embed_text(query)
            
            # Search in vector store
            search_results = self.vector_store.search(query_embedding, top_k)
            
            # Format results
            formatted_results = []
            for doc, similarity in search_results:
                formatted_results.append({
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "similarity": similarity,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                })
            
            self._logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
        except Exception as e:
            self._logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        try:
            doc = self.vector_store.get_document(doc_id)
            if doc:
                return {
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                }
            return None
        except Exception as e:
            self._logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    async def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the knowledge base"""
        try:
            result = self.vector_store.remove_document(doc_id)
            if result:
                self._logger.info(f"Removed document {doc_id} from knowledge base")
            else:
                self._logger.warning(f"Document {doc_id} not found in knowledge base")
            return result
        except Exception as e:
            self._logger.error(f"Error removing document {doc_id}: {e}")
            return False
    
    async def clear(self):
        """Clear all documents from the knowledge base"""
        self.vector_store.clear()
        self._logger.info("Knowledge base cleared")


# Global knowledge base instance
knowledge_base = KnowledgeBase()


def get_knowledge_base() -> KnowledgeBase:
    """Get the global knowledge base instance"""
    return knowledge_base