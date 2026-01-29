"""
Retriever implementation for the RAG system.
Handles retrieval of relevant documents based on queries.
"""
import asyncio
from typing import List, Dict, Any, Optional
from .knowledge_base import KnowledgeBase, get_knowledge_base
from .vector_store import Document
from ..utils.logger import get_logger


class RetrievalResult:
    """Represents a retrieval result"""
    def __init__(self, content: str, metadata: Dict[str, Any], score: float, source: str = ""):
        self.content = content
        self.metadata = metadata
        self.score = score
        self.source = source


class Retriever:
    """Retriever for fetching relevant documents based on queries"""
    
    def __init__(self):
        self.knowledge_base = get_knowledge_base()
        self._logger = get_logger(__name__)
    
    async def retrieve(self, query: str, top_k: int = 5, min_score: float = 0.0) -> List[RetrievalResult]:
        """Retrieve relevant documents for a query"""
        try:
            # Search in knowledge base
            search_results = await self.knowledge_base.search(query, top_k)
            
            # Filter by minimum score and convert to RetrievalResult objects
            filtered_results = []
            for result in search_results:
                if result["similarity"] >= min_score:
                    retrieval_result = RetrievalResult(
                        content=result["content"],
                        metadata=result["metadata"],
                        score=result["similarity"],
                        source=result.get("id", "")
                    )
                    filtered_results.append(retrieval_result)
            
            self._logger.info(f"Retrieved {len(filtered_results)} results for query: {query[:50]}...")
            return filtered_results
        except Exception as e:
            self._logger.error(f"Error retrieving documents for query '{query}': {e}")
            return []
    
    async def retrieve_with_context(self, query: str, context_size: int = 3, top_k: int = 5) -> List[RetrievalResult]:
        """Retrieve documents with additional context from surrounding content"""
        # For now, just return regular retrieval results
        # In a more advanced implementation, this would include surrounding context
        return await self.retrieve(query, top_k)
    
    async def retrieve_multiple_queries(self, queries: List[str], top_k: int = 3) -> List[RetrievalResult]:
        """Retrieve documents for multiple queries and merge results"""
        all_results = []
        
        for query in queries:
            results = await self.retrieve(query, top_k)
            all_results.extend(results)
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        # Remove duplicates based on content
        seen_contents = set()
        unique_results = []
        for result in all_results:
            content_hash = hash(result.content)
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        return unique_results


# Global retriever instance
retriever = Retriever()


def get_retriever() -> Retriever:
    """Get the global retriever instance"""
    return retriever