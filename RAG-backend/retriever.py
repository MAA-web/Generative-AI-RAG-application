"""
Retrieval module for vector similarity search.

This module implements semantic search using FAISS (Facebook AI Similarity Search)
for efficient vector-based retrieval. It:
1. Generates embeddings using sentence transformers
2. Stores vectors in a FAISS index
3. Performs fast similarity search for query retrieval
4. Persists the index to disk for reuse

The retriever uses cosine similarity (via L2 normalization) to find the most
semantically similar document chunks to a given query.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
import faiss

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install it for embeddings.")


class Retriever:
    """
    Vector-based retriever using FAISS for semantic search.
    
    Converts text documents into vector embeddings and uses FAISS for fast
    similarity search. Supports persistent storage of the vector index.
    """
    
    def __init__(self, embeddings_model: str = 'sentence-transformers/all-MiniLM-L6-v2', 
                 vector_db_path: str = 'vector_db'):
        """
        Initialize retriever.
        
        Args:
            embeddings_model: Model name for sentence transformers
            vector_db_path: Path to store vector database
        """
        self.embeddings_model_name = embeddings_model
        self.vector_db_path = vector_db_path
        os.makedirs(vector_db_path, exist_ok=True)
        
        # Initialize embeddings model
        if EMBEDDINGS_AVAILABLE:
            print(f"Loading embeddings model: {embeddings_model}")
            self.embeddings_model = SentenceTransformer(embeddings_model)
            self.embedding_dim = self.embeddings_model.get_sentence_embedding_dimension()
        else:
            raise ValueError("sentence-transformers is required. Install it with: pip install sentence-transformers")
        
        # Initialize FAISS index
        self.index = None
        self.chunks = []  # Store chunk metadata
        self.index_path = os.path.join(vector_db_path, 'faiss_index.bin')
        self.chunks_path = os.path.join(vector_db_path, 'chunks.pkl')
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """
        Load existing FAISS index and chunk metadata from disk.
        
        Attempts to load a previously saved index. If loading fails or
        files don't exist, creates a new empty index.
        """
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            try:
                # Load FAISS index binary file
                self.index = faiss.read_index(self.index_path)
                # Load chunk metadata from pickle file
                with open(self.chunks_path, 'rb') as f:
                    self.chunks = pickle.load(f)
                print(f"Loaded existing index with {len(self.chunks)} chunks")
            except Exception as e:
                # If loading fails, create new index
                print(f"Failed to load existing index: {e}. Creating new index.")
                self._create_new_index()
        else:
            # No existing index found, create new one
            self._create_new_index()
    
    def _create_new_index(self):
        """
        Create a new empty FAISS index.
        
        Initializes an L2 (Euclidean distance) index. After normalization,
        this effectively becomes cosine similarity search.
        """
        # Start with L2 index - will switch to Inner Product after normalization
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.chunks = []  # Initialize empty chunk storage
        print("Created new FAISS index")
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add documents to the vector database.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        # Step 1: Generate embeddings for all chunk texts
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embeddings_model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Step 2: Normalize vectors for cosine similarity
        # After normalization, L2 distance becomes equivalent to cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Step 3: Initialize or update index
        if self.index.ntotal == 0:
            # First batch - switch to Inner Product index for normalized vectors
            # Inner Product on normalized vectors = cosine similarity
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        else:
            # Verify embedding dimensions match existing index
            if embeddings.shape[1] != self.index.d:
                raise ValueError(f"Embedding dimension mismatch: {embeddings.shape[1]} vs {self.index.d}")
        
        # Step 4: Add embeddings to FAISS index
        self.index.add(embeddings)
        
        # Step 5: Store chunk metadata (text, source, etc.) for later retrieval
        for chunk in chunks:
            self.chunks.append(chunk)
        
        # Step 6: Persist index and metadata to disk
        self._save_index()
        
        return len(chunks)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most semantically similar chunks for a query.
        
        Performs semantic search by:
        1. Converting query to embedding vector
        2. Searching FAISS index for similar vectors
        3. Returning corresponding chunks with similarity scores
        
        Args:
            query: User question or search query text
            top_k: Number of most similar chunks to return
            
        Returns:
            List of chunk dictionaries, each containing:
                - text: Chunk text content
                - metadata: Source document information
                - chunk_id: Unique chunk identifier
                - score: Similarity score (higher = more similar)
                
        Note:
            Returns empty list if index is empty. Scores are similarity scores
            (higher values indicate better matches) since we use normalized vectors.
        """
        # Return early if no documents are indexed
        if self.index.ntotal == 0:
            return []
        
        # Step 1: Convert query text to embedding vector
        query_embedding = self.embeddings_model.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Step 2: Normalize query embedding (same as document embeddings)
        faiss.normalize_L2(query_embedding)
        
        # Step 3: Search FAISS index for most similar vectors
        top_k = min(top_k, self.index.ntotal)  # Can't retrieve more than what's indexed
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Step 4: Retrieve corresponding chunks and add similarity scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()  # Copy to avoid modifying original
                # For normalized vectors with Inner Product, higher score = more similar
                chunk['score'] = float(distances[0][i])
                results.append(chunk)
        
        return results
    
    def _save_index(self):
        """
        Persist FAISS index and chunk metadata to disk.
        
        Saves the vector index and chunk metadata so they can be loaded
        on subsequent runs without re-indexing all documents.
        """
        try:
            # Save FAISS index as binary file
            faiss.write_index(self.index, self.index_path)
            # Save chunk metadata as pickle file
            with open(self.chunks_path, 'wb') as f:
                pickle.dump(self.chunks, f)
        except Exception as e:
            # Log warning but don't fail - index is still in memory
            print(f"Warning: Failed to save index: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        return {
            'total_chunks': len(self.chunks),
            'index_size': self.index.ntotal if self.index else 0,
            'embedding_dimension': self.embedding_dim,
            'model': self.embeddings_model_name
        }
    
    def clear(self):
        """Clear the vector database."""
        self._create_new_index()
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.chunks_path):
            os.remove(self.chunks_path)

