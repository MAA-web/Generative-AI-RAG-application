"""
Flask API server for RAG-based e-commerce policy system.

This module provides a RESTful API for a Retrieval-Augmented Generation (RAG) system
designed to answer questions about Micro Center's store policies. The system supports:

- Document ingestion (PDF, TXT, MD files)
- Vector-based semantic search using FAISS
- LLM-powered answer generation with citations
- Optional web search integration
- Evaluation metrics for system performance

Main Components:
    - DocumentProcessor: Handles file parsing and chunking
    - RAGPipeline: Orchestrates retrieval and generation
    - Evaluator: Provides evaluation metrics
    - WebSearch: Optional web search integration

Author: RAG Backend System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from rag_pipeline import RAGPipeline
from evaluation import Evaluator

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application with CORS enabled for frontend integration
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend applications

# ============================================================================
# CONFIGURATION
# ============================================================================

# File system paths
UPLOAD_FOLDER = 'documents'  # Directory for uploaded documents
VECTOR_DB_PATH = 'vector_db'  # Directory for FAISS vector database files
DOCUMENTS_DIR = os.getenv('DOCUMENTS_DIR', UPLOAD_FOLDER)  # Directory to scan for auto-loading

# Embedding model configuration
EMBEDDINGS_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'  # Sentence transformer model for embeddings

# Document chunking configuration
CHUNK_SIZE = 700  # Maximum characters per chunk
CHUNK_OVERLAP = 10  # Overlap between chunks in characters (helps maintain context)

# Retrieval configuration
TOP_K = 5  # Default number of chunks to retrieve for each query

# LLM configuration
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')  # Options: 'gemini', 'openai', 'anthropic'
LLM_API_KEY = os.getenv('LLM_API_KEY', None)  # API key for LLM provider

# Auto-load configuration
# AUTO_LOAD_DOCS = os.getenv('AUTO_LOAD_DOCS', 'false').lower() == 'true'  # Auto-load on startup
AUTO_LOAD_DOCS = True  # Currently hardcoded to True for convenience

# Debug output for configuration
print(LLM_PROVIDER)
print(LLM_API_KEY) 

# ============================================================================
# INITIALIZATION
# ============================================================================

# Create necessary directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Initialize document processor for parsing and chunking documents
document_processor = DocumentProcessor(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

# Web search configuration (optional feature)
ENABLE_WEB_SEARCH = os.getenv('ENABLE_WEB_SEARCH', 'false').lower() == 'true'
WEB_SEARCH_PROVIDER = os.getenv('WEB_SEARCH_PROVIDER', 'duckduckgo')  # Options: 'google', 'bing', 'duckduckgo'
WEB_SEARCH_API_KEY = os.getenv('SEARCH_API_KEY', None)  # API key for Google/Bing (not needed for DuckDuckGo)
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID', None)  # Required for Google Custom Search

# Initialize RAG pipeline - core component that orchestrates retrieval and generation
rag_pipeline = RAGPipeline(
    embeddings_model=EMBEDDINGS_MODEL,
    vector_db_path=VECTOR_DB_PATH,
    top_k=TOP_K,
    llm_provider=LLM_PROVIDER,
    llm_api_key=LLM_API_KEY,
    enable_web_search=ENABLE_WEB_SEARCH,
    web_search_provider=WEB_SEARCH_PROVIDER,
    web_search_api_key=WEB_SEARCH_API_KEY
)

# Initialize evaluator for system performance metrics
evaluator = Evaluator(rag_pipeline)


def find_files(directory: str) -> List[str]:
    """
    Recursively find all supported document files in a directory.
    
    Scans the directory tree for PDF, TXT, and MD files. Used for auto-loading
    documents from a directory.
    
    Args:
        directory: Directory path to scan (can be absolute or relative)
        
    Returns:
        List of file paths (sorted alphabetically). Returns empty list if
        directory doesn't exist or contains no supported files.
        
    Example:
        >>> find_files('documents')
        ['documents/policy1.pdf', 'documents/policy2.txt', 'documents/subdir/policy3.md']
    """
    files = []
    directory_path = Path(directory)
    
    # Return empty list if directory doesn't exist
    if not directory_path.exists():
        return files
    
    # Supported file extensions for document processing
    extensions = ['.pdf', '.txt', '.md']
    
    # Recursively search for files with supported extensions
    for ext in extensions:
        files.extend(directory_path.rglob(f'*{ext}'))
    
    # Convert Path objects to strings and sort alphabetically
    return sorted([str(f) for f in files])


def load_documents_from_directory(directory: str, skip_existing: bool = True) -> Dict[str, Any]:
    """
    Batch load all documents from a directory into the vector database.
    
    Processes each file found in the directory, extracts text, chunks it,
    and adds it to the FAISS vector database. Continues processing even if
    individual files fail, collecting errors for reporting.
    
    Args:
        directory: Directory path to scan for documents
        skip_existing: Currently unused - all files are processed. Future
                      implementation could check for existing documents.
        
    Returns:
        Dictionary containing:
            - success (bool): Always True if function completes
            - processed (int): Number of files successfully processed
            - failed (int): Number of files that failed to process
            - total_files_found (int): Total files discovered
            - results (list): List of successfully processed files with metadata
            - errors (list): List of files that failed with error messages
            
    Note:
        Duplicate files will add additional chunks to the database. The system
        doesn't currently deduplicate based on file content.
    """
    # Find all supported files in the directory
    files = find_files(directory)
    
    # Return early if no files found
    if not files:
        return {
            'success': True,
            'message': f'No PDF/text files found in {directory}',
            'processed': 0,
            'failed': 0,
            'results': [],
            'errors': []
        }
    
    # Track processing results
    results = []
    errors = []
    processed_count = 0
    
    # Note: skip_existing functionality is not fully implemented
    # Currently all files are processed (duplicates will add more chunks)
    existing_sources = set()
    if skip_existing:
        try:
            stats = rag_pipeline.get_stats()
            # Future: Could check existing sources here to skip duplicates
            pass
        except:
            pass
    
    # Process each file
    for filepath in files:
        try:
            filename = os.path.basename(filepath)
            
            # Extract text and chunk the document
            chunks = document_processor.process_document(filepath)
            
            # Skip if no content was extracted
            if not chunks:
                errors.append({
                    'filename': filename,
                    'error': 'No content extracted from document'
                })
                continue
            
            # Add chunks to vector database and get document ID
            doc_id = rag_pipeline.add_documents(chunks, source=filename)
            
            # Record successful processing
            results.append({
                'document_id': doc_id,
                'chunks_created': len(chunks),
                'filename': filename,
                'filepath': filepath
            })
            processed_count += 1
            
        except Exception as e:
            # Record error but continue processing other files
            errors.append({
                'filename': os.path.basename(filepath),
                'filepath': filepath,
                'error': str(e)
            })
    
    # Return comprehensive results
    return {
        'success': True,
        'processed': processed_count,
        'failed': len(errors),
        'total_files_found': len(files),
        'results': results,
        'errors': errors
    }


@app.route('/ingest/auto', methods=['POST'])
def ingest_auto():
    """
    API endpoint: Automatically load all documents from a directory.
    
    Recursively scans a directory for PDF, TXT, and MD files, processes them,
    and adds them to the vector database. Useful for bulk ingestion.
    
    Request Body (JSON):
        {
            "directory": "path/to/directory",  // Optional, defaults to DOCUMENTS_DIR
            "skip_existing": false              // Optional, defaults to false
        }
    
    Returns:
        200 OK: Success with processing results
        400 Bad Request: Invalid directory path
        500 Internal Server Error: Processing failure
        
    Example Request:
        POST /ingest/auto
        {
            "directory": "documents",
            "skip_existing": false
        }
    """
    # Parse request body
    data = request.get_json() or {}
    directory = data.get('directory', DOCUMENTS_DIR)
    skip_existing = data.get('skip_existing', False)
    
    # Validate directory exists
    if not os.path.exists(directory):
        return jsonify({
            'error': f'Directory does not exist: {directory}'
        }), 400
    
    # Validate it's actually a directory (not a file)
    if not os.path.isdir(directory):
        return jsonify({
            'error': f'Path is not a directory: {directory}'
        }), 400
    
    # Process all files in directory
    try:
        result = load_documents_from_directory(directory, skip_existing=skip_existing)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'error': f'Auto-loading failed: {str(e)}'
        }), 500


@app.route('/ingest/list', methods=['GET'])
def list_documents():
    """
    API endpoint: List all available documents in a directory.
    
    Returns metadata about all supported files (PDF, TXT, MD) found in the
    specified directory. Useful for checking what documents are available
    before ingestion.
    
    Query Parameters:
        directory (string, optional): Directory to scan. Defaults to DOCUMENTS_DIR.
    
    Returns:
        200 OK: List of files with metadata (filename, path, size, extension, modified date)
        400 Bad Request: Directory doesn't exist
        500 Internal Server Error: Listing failure
        
    Example Request:
        GET /ingest/list?directory=documents
    """
    # Get directory from query parameter or use default
    directory = request.args.get('directory', DOCUMENTS_DIR)
    
    # Validate directory exists
    if not os.path.exists(directory):
        return jsonify({
            'error': f'Directory does not exist: {directory}'
        }), 400
    
    try:
        # Find all supported files
        files = find_files(directory)
        file_info = []
        
        # Collect metadata for each file
        for filepath in files:
            file_stat = os.stat(filepath)
            file_info.append({
                'filename': os.path.basename(filepath),
                'filepath': filepath,
                'size': file_stat.st_size,  # File size in bytes
                'extension': Path(filepath).suffix.lower(),
                'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()  # Last modification time
            })
        
        return jsonify({
            'directory': directory,
            'total_files': len(files),
            'files': file_info
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to list documents: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    API endpoint: Health check for monitoring and load balancers.
    
    Simple endpoint to verify the server is running and responsive.
    Returns current server status and timestamp.
    
    Returns:
        200 OK: Server is healthy
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:45.123456"
        }
        
    Example Request:
        GET /health
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/ingest', methods=['POST'])
def ingest_documents():
    """
    API endpoint: Upload and ingest a single document.
    
    Accepts a single file upload (PDF, TXT, or MD), processes it into chunks,
    and adds it to the vector database for retrieval.
    
    Request Format:
        Content-Type: multipart/form-data
        Form field: 'file' (required) - The document file to upload
    
    Returns:
        200 OK: Document successfully ingested
        {
            "success": true,
            "document_id": "doc_filename.pdf_15",
            "chunks_created": 15,
            "filename": "filename.pdf"
        }
        400 Bad Request: No file provided or invalid file
        500 Internal Server Error: Processing failure
        
    Example Request:
        POST /ingest
        Content-Type: multipart/form-data
        Form data: file=@document.pdf
    """
    # Validate file was provided
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Validate filename is not empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file to disk
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Extract text and create chunks from the document
        chunks = document_processor.process_document(filepath)
        
        # Add chunks to vector database and get document ID
        doc_id = rag_pipeline.add_documents(chunks, source=file.filename)
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'chunks_created': len(chunks),
            'filename': file.filename
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Ingestion failed: {str(e)}'
        }), 500


@app.route('/ingest/batch', methods=['POST'])
def ingest_batch():
    """
    API endpoint: Upload and ingest multiple documents at once.
    
    Accepts multiple file uploads, processes each one, and adds them all
    to the vector database. Continues processing even if individual files fail.
    
    Request Format:
        Content-Type: multipart/form-data
        Form field: 'files' (required) - Array of document files
    
    Returns:
        200 OK: Batch processing results
        {
            "success": true,
            "processed": 2,
            "failed": 1,
            "results": [...],  // Successfully processed files
            "errors": [...]     // Failed files with error messages
        }
        400 Bad Request: No files provided
        
    Example Request:
        POST /ingest/batch
        Content-Type: multipart/form-data
        Form data: files=@doc1.pdf, files=@doc2.txt, files=@doc3.md
    """
    # Validate files were provided
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    # Track processing results
    results = []
    errors = []
    
    # Process each file
    for file in files:
        # Skip empty filenames
        if file.filename == '':
            continue
        
        try:
            # Save file to disk
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            
            # Process document into chunks
            chunks = document_processor.process_document(filepath)
            
            # Add to vector database
            doc_id = rag_pipeline.add_documents(chunks, source=file.filename)
            
            # Record success
            results.append({
                'document_id': doc_id,
                'chunks_created': len(chunks),
                'filename': file.filename
            })
        except Exception as e:
            # Record error but continue processing other files
            errors.append({
                'filename': file.filename,
                'error': str(e)
            })
    
    # Return batch processing summary
    return jsonify({
        'success': True,
        'processed': len(results),
        'failed': len(errors),
        'results': results,
        'errors': errors
    }), 200


@app.route('/query', methods=['POST'])
def query():
    """
    API endpoint: Query the RAG system with a question.
    
    Main endpoint for asking questions about policy documents. Retrieves relevant
    chunks from the vector database, optionally supplements with web search,
    and generates an AI-powered answer with citations.
    
    Request Body (JSON):
        {
            "question": "What is the return policy?",  // Required
            "top_k": 5,                                // Optional, number of chunks to retrieve
            "use_web_search": false                    // Optional, enable web search integration
        }
    
    Returns:
        200 OK: Answer with citations and retrieved chunks
        {
            "question": "...",
            "answer": "...",
            "citations": [...],
            "retrieved_chunks": [...],
            "web_results": [...]  // Only if use_web_search is true
        }
        400 Bad Request: Question not provided
        500 Internal Server Error: Query processing failure
        
    Example Request:
        POST /query
        {
            "question": "What is Micro Center's return policy?",
            "top_k": 5,
            "use_web_search": true
        }
    """
    # Parse and validate request
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'Question is required'}), 400
    
    question = data['question']
    top_k = data.get('top_k', TOP_K)  # Use default if not specified
    use_web_search = data.get('use_web_search', False)  # Web search is optional
    
    try:
        # Step 1: Retrieve relevant document chunks using semantic search
        retrieved_chunks = rag_pipeline.retrieve(question, top_k=top_k)
        
        # Step 2: Optionally perform web search to supplement local documents
        web_results = None
        if use_web_search and rag_pipeline.enable_web_search and rag_pipeline.web_search:
            try:
                # Search web with site filter for Micro Center
                web_results = rag_pipeline.web_search.search(
                    question, 
                    num_results=3, 
                    site_filter='microcenter.com'
                )
            except Exception as e:
                # Log error but continue without web results
                print(f"Web search failed: {e}")
                web_results = []
        
        # Step 3: Generate answer using LLM with retrieved context
        answer, citations = rag_pipeline.generate_answer(
            question=question,
            context_chunks=retrieved_chunks,
            use_web_search=use_web_search,
            web_results=web_results
        )
        
        # Step 4: Add policy disclaimer to answer
        answer_with_disclaimer = rag_pipeline.add_safety_disclaimer(answer)
        
        # Build response with answer and metadata
        response = {
            'question': question,
            'answer': answer_with_disclaimer,
            'citations': citations,  # Both document and web citations
            'retrieved_chunks': [
                {
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'][:200] + '...',  # Truncated preview for response
                    'source': chunk['metadata']['source'],
                    'page': chunk['metadata'].get('page', 'N/A'),
                    'score': chunk.get('score', 0.0)  # Similarity score
                }
                for chunk in retrieved_chunks
            ]
        }
        
        # Add web search results if web search was used
        if use_web_search and web_results:
            response['web_results'] = [
                {
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'url': result.get('url', '')
                }
                for result in web_results
            ]
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Query failed: {str(e)}'
        }), 500


@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    API endpoint: Run evaluation metrics on the RAG system.
    
    Evaluates system performance using test questions. Calculates retrieval
    metrics (precision, recall) and faithfulness scores (how well answers
    are grounded in retrieved context).
    
    Request Body (JSON):
        {
            "test_questions": [  // Optional, uses default if not provided
                {
                    "question": "...",
                    "expected_keywords": [...],
                    "category": "..."
                }
            ]
        }
    
    Returns:
        200 OK: Evaluation results with metrics
        500 Internal Server Error: Evaluation failure
        
    Example Request:
        POST /evaluate
        {
            "test_questions": [
                {
                    "question": "What is the return policy?",
                    "expected_keywords": ["return", "policy"]
                }
            ]
        }
    """
    data = request.get_json() or {}
    test_questions = data.get('test_questions', None)  # None uses default questions
    
    try:
        results = evaluator.evaluate(test_questions)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({
            'error': f'Evaluation failed: {str(e)}'
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    API endpoint: Get statistics about the vector database.
    
    Returns information about the current state of the vector database,
    including total chunks, index size, and model information.
    
    Returns:
        200 OK: Statistics about the vector database
        {
            "total_chunks": 150,
            "index_size": 150,
            "embedding_dimension": 384,
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        }
        500 Internal Server Error: Failed to retrieve stats
        
    Example Request:
        GET /stats
    """
    try:
        stats = rag_pipeline.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to get stats: {str(e)}'
        }), 500


@app.route('/search', methods=['POST'])
def search():
    """
    API endpoint: Search for similar document chunks without generating an answer.
    
    Performs semantic search on the vector database and returns matching chunks
    with similarity scores. Useful for debugging retrieval or exploring the
    knowledge base without LLM generation.
    
    Request Body (JSON):
        {
            "query": "return policy",  // Required
            "top_k": 5                 // Optional, defaults to TOP_K
        }
    
    Returns:
        200 OK: List of matching chunks with scores
        400 Bad Request: Query not provided
        500 Internal Server Error: Search failure
        
    Example Request:
        POST /search
        {
            "query": "return policy",
            "top_k": 5
        }
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    query_text = data['query']
    top_k = data.get('top_k', TOP_K)
    
    try:
        # Retrieve similar chunks using semantic search
        results = rag_pipeline.retrieve(query_text, top_k=top_k)
        
        return jsonify({
            'query': query_text,
            'results': [
                {
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'],  # Full text (not truncated)
                    'source': chunk['metadata']['source'],
                    'page': chunk['metadata'].get('page', 'N/A'),
                    'score': chunk.get('score', 0.0)  # Similarity score
                }
                for chunk in results
            ]
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Search failed: {str(e)}'
        }), 500


@app.route('/search/web', methods=['POST'])
def web_search():
    """
    API endpoint: Search the web for information.
    
    Performs web search using the configured search provider (Google, Bing, or
    DuckDuckGo). Can be used standalone or combined with local document retrieval.
    
    Request Body (JSON):
        {
            "query": "Micro Center return policy",  // Required
            "num_results": 5,                       // Optional, defaults to 5
            "site_filter": "microcenter.com"        // Optional, filter to specific domain
        }
    
    Returns:
        200 OK: Web search results
        400 Bad Request: Web search not enabled or query not provided
        500 Internal Server Error: Web search failure
        
    Example Request:
        POST /search/web
        {
            "query": "Micro Center return policy",
            "num_results": 5,
            "site_filter": "microcenter.com"
        }
        
    Note:
        Requires ENABLE_WEB_SEARCH=true and appropriate API keys configured.
        See WEB_SEARCH_SETUP.md for configuration details.
    """
    # Check if web search is enabled
    if not rag_pipeline.enable_web_search or not rag_pipeline.web_search:
        return jsonify({
            'error': 'Web search is not enabled. Set ENABLE_WEB_SEARCH=true and configure search API keys.'
        }), 400
    
    # Parse and validate request
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    query_text = data['query']
    num_results = data.get('num_results', 5)
    site_filter = data.get('site_filter', 'microcenter.com')  # Default to Micro Center site
    
    try:
        # Perform web search
        results = rag_pipeline.web_search.search(
            query_text, 
            num_results=num_results, 
            site_filter=site_filter
        )
        
        return jsonify({
            'query': query_text,
            'num_results': len(results),
            'results': results
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Web search failed: {str(e)}'
        }), 500


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == '__main__':
    """
    Main entry point for the Flask server.
    
    Initializes the server, optionally auto-loads documents, and starts
    the Flask development server on port 5000.
    """
    # Print startup configuration
    print("Starting RAG Backend Server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Documents directory: {DOCUMENTS_DIR}")
    print(f"Vector DB path: {VECTOR_DB_PATH}")
    print(f"Embeddings model: {EMBEDDINGS_MODEL}")
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"LLM API Key: {'Set' if LLM_API_KEY else 'Not set (will use fallback)'}")
    print(f"Auto-load documents: {AUTO_LOAD_DOCS}")
    
    # Auto-load documents on startup if enabled
    if AUTO_LOAD_DOCS:
        print(f"\nAuto-loading documents from {DOCUMENTS_DIR}...")
        try:
            result = load_documents_from_directory(DOCUMENTS_DIR, skip_existing=False)
            print(f"Loaded {result['processed']} documents, {result['failed']} failed")
            
            # Print errors if any occurred
            if result['errors']:
                print("Errors:")
                for error in result['errors'][:5]:  # Show first 5 errors to avoid spam
                    print(f"  - {error['filename']}: {error['error']}")
        except Exception as e:
            print(f"Warning: Auto-loading failed: {e}")
    
    # Print available API endpoints
    print("\nAPI Endpoints:")
    print("  POST /ingest - Upload documents")
    print("  POST /ingest/batch - Upload multiple documents")
    print("  POST /ingest/auto - Auto-load from directory")
    print("  GET /ingest/list - List available documents")
    print("  POST /query - Ask questions (supports web search)")
    print("  POST /search - Search chunks")
    print("  POST /search/web - Search the web")
    print("  POST /evaluate - Run evaluation")
    print("  GET /stats - Get statistics")
    print("  GET /health - Health check")
    
    # Print web search status
    print(f"\nWeb Search: {'Enabled' if ENABLE_WEB_SEARCH else 'Disabled'}")
    if ENABLE_WEB_SEARCH:
        print(f"  Provider: {WEB_SEARCH_PROVIDER}")
    
    # Start Flask development server
    print("\nServer starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)  # debug=True enables auto-reload on code changes

