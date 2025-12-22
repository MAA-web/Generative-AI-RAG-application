"""
Main RAG pipeline combining retrieval and generation.

This module implements the core Retrieval-Augmented Generation (RAG) pipeline
that orchestrates:
1. Document retrieval from vector database
2. Optional web search integration
3. LLM-powered answer generation
4. Citation extraction and formatting
5. Safety checks and disclaimers

The pipeline is designed for e-commerce policy question answering, specifically
for Micro Center store policies.
"""

import re
from typing import List, Dict, Any, Optional
from retriever import Retriever
from llm_client import LLMClient
from web_search import WebSearch



class RAGPipeline:
    """Complete RAG pipeline for e-commerce policy question answering."""
    
    def __init__(self, embeddings_model: str = 'sentence-transformers/all-MiniLM-L6-v2',
                 vector_db_path: str = 'vector_db',
                 top_k: int = 5,
                 llm_provider: str = 'gemini',
                 llm_api_key: Optional[str] = None,
                 enable_web_search: bool = False,
                 web_search_provider: str = 'duckduckgo',
                 web_search_api_key: Optional[str] = None):
        """
        Initialize RAG pipeline.
        
        Args:
            embeddings_model: Model for generating embeddings
            vector_db_path: Path to vector database
            top_k: Default number of chunks to retrieve
            llm_provider: LLM provider ('gemini', 'openai', 'anthropic')
            llm_api_key: API key for LLM
            enable_web_search: Enable web search integration
            web_search_provider: Web search provider ('google', 'bing', 'duckduckgo')
            web_search_api_key: API key for web search (if required)
        """
        self.retriever = Retriever(embeddings_model, vector_db_path)
        self.llm_client = LLMClient(provider=llm_provider, api_key=llm_api_key)
        self.top_k = top_k
        self.enable_web_search = enable_web_search
        
        if enable_web_search:
            try:
                self.web_search = WebSearch(
                    provider=web_search_provider,
                    api_key=web_search_api_key
                )
            except Exception as e:
                print(f"Warning: Web search initialization failed: {e}")
                self.web_search = None
                self.enable_web_search = False
        else:
            self.web_search = None
    
    def add_documents(self, chunks: List[Dict[str, Any]], source: str) -> str:
        """
        Add documents to the vector database.
        
        Args:
            chunks: List of chunk dictionaries
            source: Source document name
            
        Returns:
            Document ID
        """
        # Update source metadata if needed
        for chunk in chunks:
            if 'metadata' not in chunk:
                chunk['metadata'] = {}
            chunk['metadata']['source'] = source
        
        num_added = self.retriever.add_documents(chunks)
        return f"doc_{source}_{num_added}"
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with scores
        """
        if top_k is None:
            top_k = self.top_k
        
        return self.retriever.retrieve(query, top_k=top_k)
    
    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]], 
                       use_web_search: bool = False, web_results: Optional[List[Dict[str, Any]]] = None) -> tuple[str, List[str]]:
        """
        Generate answer using retrieved context, optionally with web search results.
        
        Args:
            question: User question
            context_chunks: Retrieved chunks
            use_web_search: Whether to include web search results
            web_results: Pre-fetched web search results (optional)
            
        Returns:
            Tuple of (answer, citations)
        """
        # Check for safety concerns
        safety_response = self._check_safety(question)
        if safety_response:
            return safety_response, []
        
        # Build context from chunks
        context = self._build_context(context_chunks)
        
        # Add web search results if enabled
        web_context = ""
        web_citations = []
        if use_web_search and self.enable_web_search and self.web_search:
            if web_results is None:
                # Perform web search
                web_results = self.web_search.search(question, num_results=3, site_filter='microcenter.com')
            
            if web_results:
                web_context = self.web_search.format_search_results_as_context(web_results)
                web_citations = [result.get('url', '') for result in web_results]
                context = f"{context}\n\n---\n\n[Web Search Results]\n{web_context}" if context else web_context
        
        # Generate answer
        try:
            print(question)
            print(context)
            print("--------------------------------")
            answer = self.llm_client.generate(
                prompt=question,
                context=context,
                max_tokens=512
            )
        except Exception as e:
            answer = f"I apologize, but I encountered an error generating a response: {str(e)}. Please try again or contact Micro Center customer service for assistance."
        
        # Extract citations
        citations = self._extract_citations(context_chunks)
        citations.extend(web_citations)
        
        # Add citations to answer if not already present
        answer = self._add_citations_to_answer(answer, citations)
        
        return answer, citations
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build formatted context string from retrieved chunks.
        
        Combines multiple document chunks into a single context string
        that can be passed to the LLM. Each chunk is labeled with its
        source document for citation purposes.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            
        Returns:
            Formatted context string with document labels and separators
            
        Example:
            "[Document 1: policy.pdf]\nReturn policy text...\n\n---\n[Document 2: policy2.txt]\n..."
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk['metadata'].get('source', 'Unknown')
            text = chunk['text']
            # Format each chunk with source information
            context_parts.append(f"[Document {i}: {source}]\n{text}\n")
        # Join chunks with separator for clarity
        return "\n---\n".join(context_parts)
    
    def _extract_citations(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Extract unique citation information from retrieved chunks.
        
        Creates a list of citations, one per unique source document,
        to be included in the answer for traceability.
        
        Args:
            chunks: List of chunk dictionaries with metadata
            
        Returns:
            List of citation strings in format "source (chunk: chunk_id)"
            
        Note:
            Only includes each source once, even if multiple chunks come from
            the same document.
        """
        citations = []
        seen_sources = set()  # Track sources to avoid duplicates
        
        for chunk in chunks:
            source = chunk['metadata'].get('source', 'Unknown')
            chunk_id = chunk.get('chunk_id', '')
            
            # Add citation only if we haven't seen this source before
            if source not in seen_sources:
                citations.append(f"{source} (chunk: {chunk_id})")
                seen_sources.add(source)
        
        return citations
    
    def _add_citations_to_answer(self, answer: str, citations: List[str]) -> str:
        """
        Add citation list to answer if not already present.
        
        Appends a formatted list of sources to the answer for transparency.
        Checks if citations are already included to avoid duplication.
        
        Args:
            answer: Generated answer text
            citations: List of citation strings
            
        Returns:
            Answer with citations appended (if not already present)
        """
        # Check if citations are already in the answer (LLM might have included them)
        if any(citation in answer for citation in citations):
            return answer
        
        # Add formatted citations at the end
        if citations:
            citation_text = "\n\nSources:\n" + "\n".join(f"- {cite}" for cite in citations)
            answer += citation_text
        
        return answer
    
    def _check_safety(self, question: str) -> Optional[str]:
        """Check if question is out of scope for policy information."""
        question_lower = question.lower()
        
        # Check for questions outside of policy scope (e.g., medical, legal advice)
        out_of_scope_keywords = [
            'legal advice', 'lawyer', 'sue', 'lawsuit', 'attorney',
            'medical advice', 'diagnosis', 'prescription', 'doctor'
        ]
        
        if any(keyword in question_lower for keyword in out_of_scope_keywords):
            return """I can only answer questions about Micro Center's store policies, including returns, exchanges, warranties, shipping, and general store information.

For questions outside of store policies, please:
- Contact Micro Center customer service for specific account or order inquiries
- Consult appropriate professionals for legal or medical matters

How can I help you with Micro Center's policies today?"""
        
        return None
    
    def add_safety_disclaimer(self, answer: str) -> str:
        """Add general policy disclaimer to answer."""
        disclaimer = """

---
ℹ️ Policy Information: This information is based on Micro Center's current policies as documented. Policies may change, and specific situations may vary. For the most up-to-date information or questions about your specific order, please contact Micro Center customer service."""
        
        if disclaimer not in answer:
            answer += disclaimer
        
        return answer
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return self.retriever.get_stats()

