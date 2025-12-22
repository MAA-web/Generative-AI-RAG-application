# RAG Backend System for E-Commerce Policies

A complete Retrieval-Augmented Generation (RAG) system for answering questions about Micro Center's store policies. This system implements document ingestion, vector-based retrieval, and LLM-powered answer generation to help customers understand return policies, warranties, shipping, and other store information.

## Features

- **Document Ingestion**: Process PDF and text files with intelligent chunking and metadata extraction
- **Vector Database**: FAISS-based vector search with sentence transformer embeddings
- **Retrieval**: Top-k similarity search with retrieval metrics
- **Answer Generation**: LLM-powered answers using retrieved context with citations
- **Safety Features**: Policy disclaimers and scope management for e-commerce questions
- **Evaluation Framework**: Comprehensive evaluation with retrieval and faithfulness metrics

## Setup

### Prerequisites

- Python 3.8 or higher
- pip or conda package manager

### Installation

1. Install dependencies:
```bash
cd RAG-backend
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
# For Gemini API (uses google-genai SDK)
export GEMINI_API_KEY="your-gemini-api-key"
# Or use LLM_API_KEY for backward compatibility
export LLM_API_KEY="your-gemini-api-key"

# Or for OpenAI
export LLM_API_KEY="your-openai-api-key"

# Optional: Auto-load documents on startup
export AUTO_LOAD_DOCS=true
export DOCUMENTS_DIR="/path/to/your/pdf/documents"

# Optional: Enable web search (see WEB_SEARCH_SETUP.md for details)
export ENABLE_WEB_SEARCH=true
export WEB_SEARCH_PROVIDER=duckduckgo  # 'duckduckgo', 'google', or 'bing'
export SEARCH_API_KEY="your-search-api-key"  # Required for Google/Bing
export GOOGLE_SEARCH_ENGINE_ID="your-engine-id"  # Required for Google
```

3. Create necessary directories:
```bash
mkdir -p documents vector_db
```

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

#### 2. Ingest Documents

**Single document:**
```bash
curl -X POST http://localhost:5000/ingest \
  -F "file=@path/to/document.pdf"
```

**Multiple documents:**
```bash
curl -X POST http://localhost:5000/ingest/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```

**Auto-load from directory:**
```bash
# Load all PDF/text files from a directory
curl -X POST http://localhost:5000/ingest/auto \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "path/to/documents",
    "skip_existing": false
  }'

# Or use default documents folder
curl -X POST http://localhost:5000/ingest/auto
```

**List available documents:**
```bash
# List all PDF/text files in a directory
curl "http://localhost:5000/ingest/list?directory=path/to/documents"

# Or use default documents folder
curl http://localhost:5000/ingest/list
```

#### 3. Query the System

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Micro Center's return policy?",
    "top_k": 5
  }'
```

Response includes:
- `answer`: Generated answer with citations
- `citations`: List of source documents
- `retrieved_chunks`: Retrieved context chunks with scores

#### 4. Search (Retrieval Only)

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "prevention guidelines",
    "top_k": 5
  }'
```

#### 5. Get Statistics

```bash
curl http://localhost:5000/stats
```

#### 6. Run Evaluation

```bash
curl -X POST http://localhost:5000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "test_questions": [
      {
        "question": "What is the return policy?",
        "expected_keywords": ["return", "policy", "refund"]
      }
    ]
  }'
```

Or use default test questions:
```bash
curl -X POST http://localhost:5000/evaluate
```

## Configuration

Edit `main.py` or set environment variables to customize:

- `CHUNK_SIZE`: Characters per chunk (default: 512)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `TOP_K`: Default number of retrieved chunks (default: 5)
- `EMBEDDINGS_MODEL`: Sentence transformer model (default: 'all-MiniLM-L6-v2')
- `llm_provider`: LLM provider - 'gemini', 'openai', or 'anthropic'
- `AUTO_LOAD_DOCS`: Auto-load documents on startup (default: 'false')
  ```bash
  export AUTO_LOAD_DOCS=true
  ```
- `DOCUMENTS_DIR`: Directory to scan for PDFs (default: 'documents')
  ```bash
  export DOCUMENTS_DIR=/path/to/your/documents
  ```

## LLM Providers

The system supports multiple LLM providers via API calls:

### Gemini (Google)
```python
# Set environment variable
export LLM_API_KEY="your-gemini-api-key"
```

### OpenAI
```python
# Set environment variable
export LLM_API_KEY="your-openai-api-key"
# Edit rag_pipeline.py to use 'openai' as provider
```

### Anthropic Claude
```python
# Set environment variable
export LLM_API_KEY="your-anthropic-api-key"
# Edit rag_pipeline.py to use 'anthropic' as provider
```

## Safety Features

The system automatically:
- Focuses on policy-related questions
- Redirects out-of-scope questions (legal/medical advice)
- Adds policy disclaimers to all answers
- Suggests contacting customer service for specific inquiries

## Evaluation

The evaluation framework provides:
- **Retrieval Metrics**: Precision@k, Recall@k, average similarity scores
- **Faithfulness Metrics**: How well answers are grounded in retrieved context
- **Overall Statistics**: Aggregate metrics across test questions

## Project Structure

```
RAG-backend/
├── main.py                 # Flask API server
├── document_processor.py  # PDF/text processing and chunking
├── retriever.py           # Vector search with FAISS
├── llm_client.py          # LLM API client
├── rag_pipeline.py        # Main RAG pipeline
├── evaluation.py          # Evaluation framework
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Data Sources

This system is designed to work with Micro Center's policy documents, including:
- Return and refund policies
- Exchange policies
- Warranty information
- Shipping and delivery policies
- Store-specific information

**Note**: Ensure you have permission to use any policy documents you load into the system.

## Troubleshooting

### PDF Processing Issues
- Install `pdfplumber` for better PDF extraction: `pip install pdfplumber`
- Ensure PDFs are not password-protected or corrupted

### Embeddings Issues
- First run will download the sentence transformer model (may take time)
- Ensure sufficient disk space for model cache

### LLM API Issues
- Verify API key is set correctly
- Check API rate limits and quotas
- Ensure internet connection for API calls

## License

This project is for educational purposes. Ensure you have proper authorization to use any policy documents you load into the system.

