"""
RAG (Retrieval-Augmented Generation) module for the agency system.
Provides knowledge retrieval and storage capabilities.
"""
from .vector_store import VectorStore, get_vector_store
from .knowledge_base import KnowledgeBase, get_knowledge_base
from .retriever import Retriever, get_retriever
from .embeddings import EmbeddingService, get_embedding_service


def initialize_rag_system():
    """Initialize the RAG system components"""
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()
    knowledge_base = get_knowledge_base()
    retriever = get_retriever()

    return embedding_service, vector_store, knowledge_base, retriever