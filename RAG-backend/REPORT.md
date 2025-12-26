# RAG Backend System - Technical Report

## Executive Summary

The RAG (Retrieval-Augmented Generation) Backend is a comprehensive Flask-based API server designed for e-commerce policy question answering, specifically tailored for Micro Center's store policies. The system combines vector-based semantic search with large language model (LLM) generation to provide accurate, cited answers to customer questions about return policies, warranties, shipping, and other store information.

**Key Capabilities:**
- Document ingestion from PDF, TXT, and MD files
- Semantic search using FAISS vector database
- Multi-provider LLM support (Gemini, OpenAI, Anthropic)
- Optional web search integration
- Comprehensive evaluation framework
- RESTful API with CORS support

---

## System Architecture

### High-Level Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask API Server (main.py)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Document │  │   RAG    │  │Evaluator  │  │   Web    │   │
│  │Processor │  │ Pipeline │  │           │  │  Search  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       │              │              │              │        │
│       └──────────────┼──────────────┼──────────────┘        │
│                      │              │                        │
│              ┌───────▼──────────────▼───────┐               │
│              │      Retriever (FAISS)       │               │
│              │  ┌────────────────────────┐  │               │
│              │  │  Vector Database       │  │               │
│              │  │  (Embeddings + Index)  │  │               │
│              │  └────────────────────────┘  │               │
│              └──────────────────────────────┘               │
│                      │                                      │
│              ┌───────▼──────────────┐                       │
│              │   LLM Client          │                       │
│              │ (Gemini/OpenAI/Claude)│                      │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Document Processor** (`document_processor.py`)
- **Purpose**: Handles document ingestion and text extraction
- **Capabilities**:
  - Extracts text from PDF files (using `pdfplumber` or `PyPDF2`)
  - Processes plain text and Markdown files
  - Intelligent chunking with overlap preservation
  - Text cleaning and normalization
- **Chunking Strategy**:
  - Primary: Split by paragraphs (preserves semantic boundaries)
  - Fallback: Split by sentences if chunks exceed size limit
  - Maintains configurable overlap (default: 10 characters) to preserve context
  - Default chunk size: 700 characters

#### 2. **Retriever** (`retriever.py`)
- **Purpose**: Implements vector-based semantic search
- **Technology Stack**:
  - **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2` model)
  - **Vector Database**: FAISS (Facebook AI Similarity Search)
  - **Similarity Metric**: Cosine similarity (via L2-normalized inner product)
- **Key Features**:
  - Persistent storage of vector index and chunk metadata
  - Fast similarity search (sub-millisecond for thousands of vectors)
  - Automatic index loading on startup
  - Embedding dimension: 384 (from MiniLM model)

#### 3. **RAG Pipeline** (`rag_pipeline.py`)
- **Purpose**: Orchestrates retrieval and generation workflow
- **Workflow**:
  1. Receives user question
  2. Performs safety checks (filters out-of-scope questions)
  3. Retrieves relevant document chunks
  4. Optionally performs web search
  5. Builds context from retrieved chunks
  6. Generates answer using LLM
  7. Extracts and formats citations
  8. Adds safety disclaimers
- **Safety Features**:
  - Filters questions outside policy scope (legal/medical advice)
  - Adds policy disclaimers to all answers
  - Redirects users to customer service for specific inquiries

#### 4. **LLM Client** (`llm_client.py`)
- **Purpose**: Unified interface for multiple LLM providers
- **Supported Providers**:
  - **Google Gemini**: Primary provider, uses `google-genai` SDK (preferred) or HTTP API
  - **OpenAI**: GPT-3.5-turbo via HTTP API
  - **Anthropic Claude**: Claude 3 Haiku via HTTP API
- **RAG-Specific Prompting**:
  - Instructs LLM to answer only from provided context
  - Requires citations in answers
  - Customer-friendly tone
  - Handles cases where context is insufficient

#### 5. **Web Search** (`web_search.py`)
- **Purpose**: Optional web search integration for up-to-date information
- **Supported Providers**:
  - **DuckDuckGo**: Free, no API key required (HTML scraping)
  - **Google Custom Search**: Requires API key and search engine ID
  - **Bing Web Search**: Requires Azure subscription key
- **Features**:
  - Site filtering (e.g., restrict to `microcenter.com`)
  - Result formatting for LLM context
  - Graceful fallback on failures

#### 6. **Evaluator** (`evaluation.py`)
- **Purpose**: System performance evaluation and metrics
- **Metrics**:
  - **Retrieval Metrics**:
    - Precision@k: Proportion of retrieved chunks that are relevant
    - Recall@k: Proportion of expected keywords found
    - Average similarity scores
  - **Faithfulness Metrics**:
    - Measures how well answers are grounded in retrieved context
    - Uses term overlap and citation presence
- **Test Data**: Uses `test_questions.json` with 10 predefined test cases

#### 7. **Flask API Server** (`main.py`)
- **Purpose**: RESTful API endpoints for all system operations
- **Features**:
  - CORS enabled for frontend integration
  - Auto-loading documents on startup
  - Comprehensive error handling
  - Health check endpoint

---

## How It Works: End-to-End Flow

### Document Ingestion Flow

```
1. User uploads document (PDF/TXT/MD)
   ↓
2. DocumentProcessor extracts text
   ↓
3. Text is cleaned and normalized
   ↓
4. Text is chunked with overlap
   ↓
5. Chunks are embedded using sentence transformers
   ↓
6. Embeddings are normalized (L2) for cosine similarity
   ↓
7. Vectors are added to FAISS index
   ↓
8. Chunk metadata is stored alongside vectors
   ↓
9. Index is persisted to disk
```

### Query Processing Flow

```
1. User submits question via API
   ↓
2. Safety check filters out-of-scope questions
   ↓
3. Question is embedded using same model
   ↓
4. FAISS performs similarity search (top-k)
   ↓
5. (Optional) Web search is performed
   ↓
6. Retrieved chunks + web results are formatted as context
   ↓
7. LLM generates answer from context
   ↓
8. Citations are extracted and added
   ↓
9. Safety disclaimer is appended
   ↓
10. Response is returned with answer, citations, and metadata
```

---

## API Endpoints

### Document Management

| Endpoint | Method | Purpose | Request Body |
|----------|--------|---------|--------------|
| `/ingest` | POST | Upload single document | `multipart/form-data` with `file` |
| `/ingest/batch` | POST | Upload multiple documents | `multipart/form-data` with `files[]` |
| `/ingest/auto` | POST | Auto-load from directory | `{"directory": "...", "skip_existing": false}` |
| `/ingest/list` | GET | List available documents | Query param: `?directory=...` |

### Query & Search

| Endpoint | Method | Purpose | Request Body |
|----------|--------|---------|--------------|
| `/query` | POST | Ask question (full RAG) | `{"question": "...", "top_k": 5, "use_web_search": false}` |
| `/search` | POST | Search chunks only | `{"query": "...", "top_k": 5}` |
| `/search/web` | POST | Web search only | `{"query": "...", "num_results": 5, "site_filter": "..."}` |

### System Operations

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/stats` | GET | Vector database statistics |
| `/evaluate` | POST | Run evaluation metrics |

### Example Query Response

```json
{
  "question": "What is Micro Center's return policy?",
  "answer": "Based on Micro Center's policy documents... [with citations]\n\n---\nℹ️ Policy Information: This information is based on...",
  "citations": [
    "MicroCentreReturnPolicy.txt (chunk: MicroCentreReturnPolicy.txt_chunk_0)",
    "https://www.microcenter.com/return-policy"
  ],
  "retrieved_chunks": [
    {
      "chunk_id": "MicroCentreReturnPolicy.txt_chunk_0",
      "text": "Micro Center offers a 15-day return policy...",
      "source": "MicroCentreReturnPolicy.txt",
      "page": "N/A",
      "score": 0.8234
    }
  ],
  "web_results": [...]
}
```

---

## Configuration

### Environment Variables

```bash
# LLM Configuration
LLM_PROVIDER=gemini                    # Options: gemini, openai, anthropic
LLM_API_KEY=your-api-key              # Required for LLM generation
GEMINI_API_KEY=your-gemini-key        # Alternative for Gemini

# Document Loading
AUTO_LOAD_DOCS=true                   # Auto-load documents on startup
DOCUMENTS_DIR=documents               # Directory to scan for documents

# Web Search (Optional)
ENABLE_WEB_SEARCH=false               # Enable web search integration
WEB_SEARCH_PROVIDER=duckduckgo       # Options: duckduckgo, google, bing
SEARCH_API_KEY=your-search-key        # Required for Google/Bing
GOOGLE_SEARCH_ENGINE_ID=your-id      # Required for Google Custom Search
```

### Code Configuration (in `main.py`)

```python
# Document Processing
CHUNK_SIZE = 700                      # Characters per chunk
CHUNK_OVERLAP = 10                    # Overlap between chunks

# Retrieval
TOP_K = 5                             # Default number of chunks to retrieve
EMBEDDINGS_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# File Paths
UPLOAD_FOLDER = 'documents'
VECTOR_DB_PATH = 'vector_db'
```

---

## Technical Details

### Vector Search Implementation

1. **Embedding Generation**:
   - Model: `sentence-transformers/all-MiniLM-L6-v2`
   - Dimension: 384
   - Encodes both documents and queries with the same model

2. **FAISS Index**:
   - Type: `IndexFlatIP` (Inner Product) on normalized vectors
   - Normalization: L2 normalization makes inner product = cosine similarity
   - Persistence: Index saved as `faiss_index.bin`, metadata as `chunks.pkl`

3. **Similarity Scoring**:
   - Scores range from -1 to 1 (after normalization)
   - Higher scores = more similar
   - Typical relevant chunks score > 0.7

### Chunking Strategy

The system uses a two-stage chunking approach:

1. **Paragraph-based chunking** (primary):
   - Splits on double newlines (`\n\n`)
   - Preserves semantic boundaries
   - Maintains overlap between chunks

2. **Sentence-based chunking** (fallback):
   - Used when paragraphs exceed chunk size
   - Splits on sentence boundaries (`.`, `!`, `?`)
   - Ensures no chunk exceeds size limit

**Benefits**:
- Preserves context across chunk boundaries
- Maintains semantic coherence
- Handles documents of varying structure

### LLM Prompt Engineering

The system uses carefully crafted prompts that:

1. **Instruct grounding**: "Answer using ONLY the provided context"
2. **Require citations**: "Include citations in your answer"
3. **Handle uncertainty**: "If context doesn't contain enough information, say so"
4. **Set tone**: "Be concise, accurate, and customer-friendly"
5. **Define scope**: "Focus on policies related to returns, exchanges, warranties..."

### Safety Mechanisms

1. **Question Filtering**:
   - Detects out-of-scope keywords (legal, medical advice)
   - Returns predefined response redirecting to appropriate channels

2. **Answer Disclaimers**:
   - Automatically appends policy disclaimer to all answers
   - Warns that policies may change
   - Suggests contacting customer service for specific inquiries

---

## Evaluation Framework

### Metrics

1. **Retrieval Metrics**:
   - **Precision@k**: Measures relevance of retrieved chunks
   - **Recall@k**: Measures coverage of expected keywords
   - **Average Similarity Score**: Quality of matches

2. **Faithfulness Metrics**:
   - **Term Overlap**: Percentage of answer terms found in context
   - **Citation Presence**: Bonus for including source citations
   - **Score Range**: 0.0 (not grounded) to 1.0 (fully grounded)

### Test Questions

The system includes 10 predefined test questions covering:
- Return policies (5 questions)
- Warranty information (1 question)
- Exchange procedures (1 question)
- Shipping options (1 question)
- Refund processes (1 question)
- Online/in-store returns (1 question)

Each test question includes:
- Expected keywords for relevance checking
- Category classification
- Question text

---

## Dependencies

### Core Dependencies

```
flask                    # Web framework
flask-cors               # CORS support
sentence-transformers    # Embeddings generation
faiss-cpu               # Vector search (or faiss-gpu for GPU)
numpy                   # Numerical operations
torch                   # PyTorch (for sentence-transformers)
python-dotenv           # Environment variable management
```

### Document Processing

```
PyPDF2                  # PDF text extraction (fallback)
pdfplumber              # Better PDF extraction (preferred)
```

### LLM Integration

```
google-genai            # Gemini SDK (preferred)
requests                # HTTP requests for API calls
```

### Web Search

```
beautifulsoup4          # HTML parsing for DuckDuckGo
requests                # HTTP requests
```

---

## Use Cases

### Primary Use Case: E-Commerce Policy Q&A

The system is designed for:
- **Customer Service**: Answering policy questions 24/7
- **Self-Service**: Customers finding answers without human intervention
- **Consistency**: Providing consistent policy information
- **Documentation**: Making policy documents searchable and accessible

### Example Scenarios

1. **Return Policy Questions**:
   - "How long do I have to return an item?"
   - "Can I return opened items?"
   - "What items are not eligible for return?"

2. **Warranty Information**:
   - "What is the warranty policy?"
   - "How long is the warranty period?"

3. **Shipping & Delivery**:
   - "What are the shipping options?"
   - "How long does delivery take?"

4. **Exchange Procedures**:
   - "How do I exchange an item?"
   - "Can I exchange online purchases in-store?"

---

## Strengths

1. **Modular Architecture**: Clear separation of concerns, easy to extend
2. **Multi-Provider Support**: Works with multiple LLM providers
3. **Persistent Storage**: Vector index persists across restarts
4. **Comprehensive Evaluation**: Built-in metrics for system assessment
5. **Safety Features**: Built-in filtering and disclaimers
6. **Flexible Ingestion**: Supports multiple file formats and batch operations
7. **Web Search Integration**: Optional hybrid retrieval with web results
8. **Production-Ready API**: RESTful endpoints with error handling

---

## Limitations & Considerations

1. **Chunking Strategy**: Simple character-based chunking may not always preserve semantic boundaries optimally
2. **Evaluation Metrics**: Keyword-based evaluation is simple; could be enhanced with semantic similarity
3. **Web Search**: DuckDuckGo HTML parsing may break if page structure changes
4. **No Deduplication**: System doesn't prevent duplicate document ingestion
5. **Limited Context Window**: Chunk size (700 chars) may truncate long paragraphs
6. **API Rate Limits**: LLM and web search APIs have usage limits
7. **No Authentication**: API endpoints are open (should add auth for production)

---

## Future Enhancements

1. **Advanced Chunking**: Semantic-aware chunking using NLP techniques
2. **Hybrid Search**: Combine semantic and keyword search
3. **Re-ranking**: Use cross-encoder models to re-rank retrieved chunks
4. **Conversation Memory**: Support multi-turn conversations
5. **User Feedback**: Collect and incorporate user feedback for improvement
6. **A/B Testing**: Compare different retrieval/generation strategies
7. **Analytics Dashboard**: Monitor system performance and usage
8. **Document Versioning**: Track document updates and versions
9. **Multi-language Support**: Support for non-English documents
10. **Fine-tuning**: Fine-tune embeddings model on domain-specific data

---

## Conclusion

The RAG Backend System is a well-architected, production-ready solution for document-based question answering. It successfully combines modern vector search techniques with large language models to provide accurate, cited answers to policy questions. The modular design allows for easy extension and customization, while the comprehensive evaluation framework enables continuous improvement.

The system demonstrates best practices in:
- **RAG implementation**: Proper retrieval-augmented generation workflow
- **API design**: RESTful endpoints with clear documentation
- **Error handling**: Graceful degradation and fallbacks
- **Safety**: Built-in filtering and disclaimers
- **Evaluation**: Metrics for assessing system performance

With proper configuration and deployment, this system can serve as a robust foundation for e-commerce customer service automation.

---

## Appendix: File Structure

```
RAG-backend/
├── main.py                 # Flask API server (891 lines)
├── document_processor.py  # Document processing and chunking
├── retriever.py           # FAISS vector search implementation
├── rag_pipeline.py        # Main RAG orchestration
├── llm_client.py          # Multi-provider LLM client
├── web_search.py          # Web search integration
├── evaluation.py          # Evaluation framework
├── request.py             # Example request script
├── example_usage.py       # Usage examples
├── requirements.txt       # Python dependencies
├── test_questions.json    # Evaluation test cases
├── README.md              # User documentation
├── QUICKSTART.md          # Quick start guide
├── WEB_SEARCH_SETUP.md    # Web search configuration
├── REPORT.md              # This report
├── documents/             # Document storage
│   ├── MicroCentreReturnPolicy.txt
│   └── WhatIsTheReturnPolicy.txt
└── vector_db/             # Vector database storage
    ├── faiss_index.bin    # FAISS index
    └── chunks.pkl         # Chunk metadata
```

---

*Report Generated: 2024*
*System Version: Current*
*Total Lines of Code: ~2,500+*

