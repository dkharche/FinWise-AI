"""RAG (Retrieval-Augmented Generation) service."""

import logging
import time
from typing import List, Dict, Any, Optional
from src.services.vector_store import VectorStoreService
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for document querying with retrieval and generation."""
    
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.initialized = False
    
    async def initialize(self):
        """Initialize RAG service components."""
        if not self.initialized:
            logger.info("Initializing RAG service...")
            await self.vector_store.initialize()
            self.initialized = True
            logger.info("RAG service initialized successfully")
    
    async def query(
        self,
        query: str,
        n_results: int = 5,
        model: str = "gpt-4",
        filter_dict: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Query documents using RAG.
        
        Args:
            query: User query
            n_results: Number of documents to retrieve
            model: LLM model to use
            filter_dict: Optional metadata filter
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        start_time = time.time()
        logger.info(f"Processing RAG query: {query}")
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Step 1: Retrieve relevant documents
            search_results = await self.vector_store.search(
                query=query,
                n_results=n_results,
                filter_dict=filter_dict
            )
            
            if not search_results:
                return {
                    "answer": "I couldn't find any relevant information in the documents to answer your question.",
                    "sources": [],
                    "context_used": "",
                    "processing_time": time.time() - start_time,
                    "model_used": model
                }
            
            # Step 2: Build context from retrieved documents
            context = self._build_context(search_results)
            
            # Step 3: Generate response using LLM
            prompt = self._build_prompt(query, context)
            system_message = self._get_system_message()
            
            answer = await self.llm_service.generate_response(
                prompt=prompt,
                model=model,
                system_message=system_message,
                max_tokens=1000,
                temperature=0.7
            )
            
            processing_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": search_results,
                "context_used": context,
                "processing_time": processing_time,
                "model_used": model,
                "num_sources": len(search_results)
            }
        
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            raise
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results.
        
        Args:
            search_results: List of search result dictionaries
        
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, result in enumerate(search_results, 1):
            doc_text = result['document']
            metadata = result.get('metadata', {})
            
            # Add source information
            source_info = f"Source {i}"
            if 'filename' in metadata:
                source_info += f" ({metadata['filename']})"
            if 'page' in metadata:
                source_info += f" - Page {metadata['page']}"
            
            context_parts.append(f"{source_info}:\n{doc_text}\n")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build prompt for LLM.
        
        Args:
            query: User query
            context: Retrieved context
        
        Returns:
            Formatted prompt
        """
        return f"""Based on the following context from financial documents, please answer the question accurately and concisely.

Context:
{context}

Question: {query}

Answer:"""
    
    def _get_system_message(self) -> str:
        """Get system message for LLM.
        
        Returns:
            System message string
        """
        return """You are a financial document analysis assistant. Your role is to:
1. Provide accurate answers based ONLY on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Cite specific details from the context when possible
4. Use clear, professional language
5. Format numbers and financial data appropriately
6. Never make up information not present in the context"""
    
    async def add_document_to_index(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ):
        """Add a processed document to the vector index.
        
        Args:
            document_id: Unique document identifier
            chunks: List of text chunks from the document
            metadata: Document metadata
        """
        logger.info(f"Adding document {document_id} to vector index")
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Prepare data for vector store
            texts = [chunk['text'] for chunk in chunks]
            chunk_metadatas = [
                {
                    **metadata,
                    "chunk_id": chunk['chunk_id'],
                    "document_id": document_id
                }
                for chunk in chunks
            ]
            ids = [f"{document_id}_chunk_{chunk['chunk_id']}" for chunk in chunks]
            
            # Add to vector store
            await self.vector_store.add_documents(
                texts=texts,
                metadatas=chunk_metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully indexed {len(chunks)} chunks for document {document_id}")
        
        except Exception as e:
            logger.error(f"Error adding document to index: {e}")
            raise