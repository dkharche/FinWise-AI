"""Vector store service for embeddings and retrieval."""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Manage vector embeddings and similarity search."""
    
    def __init__(self, persist_directory: str = "./data/chroma"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
    
    async def initialize(self):
        """Initialize vector database and embedding model."""
        logger.info("Initializing vector store...")
        
        try:
            # Create persist directory if it doesn't exist
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path=self.persist_directory
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="financial_documents",
                metadata={"description": "Financial document embeddings"}
            )
            
            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info(f"Vector store initialized. Collection has {self.collection.count()} documents")
        
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add documents to vector store.
        
        Args:
            texts: List of text chunks to add
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for each document
        """
        logger.info(f"Adding {len(texts)} documents to vector store")
        
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(texts)} documents")
        
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional metadata filter
        
        Returns:
            List of search results with documents and metadata
        """
        logger.info(f"Searching for: {query}")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_dict
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    async def delete_documents(self, ids: List[str]):
        """Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
        """
        logger.info(f"Deleting {len(ids)} documents")
        
        try:
            self.collection.delete(ids=ids)
            logger.info("Documents deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name,
                "embedding_dimension": self.embedding_dimension
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        logger.warning("Clearing all documents from collection")
        try:
            # Delete and recreate collection
            self.client.delete_collection(name="financial_documents")
            self.collection = self.client.create_collection(
                name="financial_documents",
                metadata={"description": "Financial document embeddings"}
            )
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise