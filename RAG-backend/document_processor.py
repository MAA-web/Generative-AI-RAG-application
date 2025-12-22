"""
Document processing module for PDF and text files.

This module handles the document ingestion pipeline:
1. Text extraction from PDF, TXT, and MD files
2. Text cleaning and normalization
3. Intelligent chunking with overlap
4. Metadata generation for traceability

The chunking strategy:
- First splits by paragraphs for semantic boundaries
- Then splits by sentences if chunks are still too large
- Maintains overlap between chunks to preserve context
"""

import os
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not available. PDF processing will be limited.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class DocumentProcessor:
    """Processes documents (PDF/text) into chunks with metadata."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Process a document file into chunks.
        
        Args:
            filepath: Path to the document file
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        file_ext = Path(filepath).suffix.lower()
        
        if file_ext == '.pdf':
            text, metadata_base = self._extract_pdf(filepath)
        elif file_ext in ['.txt', '.md']:
            text, metadata_base = self._extract_text(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Clean text
        text = self._clean_text(text)
        
        # Chunk text
        chunks = self._chunk_text(text, metadata_base)
        
        return chunks
    
    def _extract_pdf(self, filepath: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text from PDF file."""
        text_parts = []
        metadata_base = {
            'source': os.path.basename(filepath),
            'file_type': 'pdf'
        }
        
        # Try pdfplumber first (better text extraction)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(filepath) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append((page_num, page_text))
                text = '\n\n'.join([text for _, text in text_parts])
                return text, metadata_base
            except Exception as e:
                print(f"pdfplumber failed: {e}, trying PyPDF2...")
        
        # Fallback to PyPDF2
        if PDF_AVAILABLE:
            try:
                with open(filepath, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, start=1):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append((page_num, page_text))
                text = '\n\n'.join([text for _, text in text_parts])
                return text, metadata_base
            except Exception as e:
                raise ValueError(f"Failed to extract PDF: {e}")
        else:
            raise ValueError("No PDF library available. Install PyPDF2 or pdfplumber.")
    
    def _extract_text(self, filepath: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text from plain text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
            metadata_base = {
                'source': os.path.basename(filepath),
                'file_type': 'text'
            }
            return text, metadata_base
        except Exception as e:
            raise ValueError(f"Failed to extract text: {e}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Removes problematic characters, normalizes whitespace, and prepares
        text for chunking. This improves embedding quality and consistency.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and normalized text string
            
        Processing steps:
            1. Collapse multiple whitespace characters to single spaces
            2. Remove control characters that might interfere with processing
            3. Normalize multiple line breaks to double line breaks
            4. Strip leading/trailing whitespace
        """
        # Step 1: Remove excessive whitespace (multiple spaces/tabs become single space)
        text = re.sub(r'\s+', ' ', text)
        
        # Step 2: Remove control characters (except newlines and tabs)
        # These can cause issues with embeddings and LLM processing
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        
        # Step 3: Normalize line breaks (multiple blank lines become double line break)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def _chunk_text(self, text: str, metadata_base: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for vector storage.
        
        Uses a two-stage chunking strategy:
        1. Primary: Split by paragraphs (preserves semantic boundaries)
        2. Fallback: Split by sentences if chunks are still too large
        
        Maintains overlap between chunks to preserve context across boundaries.
        
        Args:
            text: Input text to chunk
            metadata_base: Base metadata (source, file_type) to include in all chunks
            
        Returns:
            List of chunk dictionaries, each containing:
                - chunk_id: Unique identifier
                - text: Chunk text content
                - metadata: Source document information
                
        Chunking Strategy:
            - Prefers paragraph boundaries for semantic coherence
            - Falls back to sentence boundaries if paragraphs are too large
            - Maintains overlap to prevent information loss at boundaries
        """
        chunks = []
        chunk_id_counter = 0
        
        # Stage 1: Split by paragraphs first (better semantic boundaries)
        paragraphs = text.split('\n\n')
        current_chunk = ""
        current_metadata = metadata_base.copy()
        
        for para in paragraphs:
            para = para.strip()
            if not para:  # Skip empty paragraphs
                continue
            
            # Check if adding this paragraph would exceed chunk size
            if len(current_chunk) + len(para) + 2 > self.chunk_size and current_chunk:
                # Finalize current chunk
                chunks.append({
                    'chunk_id': f"{metadata_base['source']}_chunk_{chunk_id_counter}",
                    'text': current_chunk.strip(),
                    'metadata': current_metadata.copy()
                })
                chunk_id_counter += 1
                
                # Start new chunk with overlap from previous chunk
                if self.chunk_overlap > 0:
                    # Take last N characters from previous chunk for overlap
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + para
                else:
                    current_chunk = para
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Add final chunk if there's remaining text
        if current_chunk:
            chunks.append({
                'chunk_id': f"{metadata_base['source']}_chunk_{chunk_id_counter}",
                'text': current_chunk.strip(),
                'metadata': current_metadata.copy()
            })
        
        # Stage 2: If any chunks are still too large, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk['text']) <= self.chunk_size:
                # Chunk is within size limit, keep as-is
                final_chunks.append(chunk)
            else:
                # Chunk too large - split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', chunk['text'])
                temp_chunk = ""
                temp_id = chunk['chunk_id']
                sentence_idx = 0
                
                # Build sentence-based chunks
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) + 1 > self.chunk_size and temp_chunk:
                        # Finalize current sentence chunk
                        final_chunks.append({
                            'chunk_id': f"{temp_id}_s{sentence_idx}",
                            'text': temp_chunk.strip(),
                            'metadata': chunk['metadata'].copy()
                        })
                        sentence_idx += 1
                        temp_chunk = sentence
                    else:
                        # Add sentence to current chunk
                        temp_chunk += " " + sentence if temp_chunk else sentence
                
                # Add final sentence chunk
                if temp_chunk:
                    final_chunks.append({
                        'chunk_id': f"{temp_id}_s{sentence_idx}",
                        'text': temp_chunk.strip(),
                        'metadata': chunk['metadata'].copy()
                    })
        
        return final_chunks

