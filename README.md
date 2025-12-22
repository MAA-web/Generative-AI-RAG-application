# API Documentation

Complete API reference for the RAG Backend System. All endpoints return JSON responses.

**Base URL**: `http://localhost:5000`

---

## 1. Health Check

Check if the server is running.

### Endpoint
```
GET /health
```

### Request
No request body or parameters required.

### Response

**Success (200 OK)**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

---

## 2. Ingest Single Document

Upload a single document (PDF, TXT, or MD) to the system.

### Endpoint
```
POST /ingest
```

### Request

**Content-Type**: `multipart/form-data`

**Form Data**:
- `file` (file, required): The document file to upload

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/ingest \
  -F "file=@document.pdf"
```

**Example (JavaScript/Fetch)**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/ingest', {
  method: 'POST',
  body: formData
})
```

### Response

**Success (200 OK)**
```json
{
  "success": true,
  "document_id": "doc_policy.pdf_15",
  "chunks_created": 15,
  "filename": "policy.pdf"
}
```

**Error (400 Bad Request)**
```json
{
  "error": "No file provided"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Ingestion failed: <error message>"
}
```

---

## 3. Ingest Multiple Documents

Upload multiple documents at once.

### Endpoint
```
POST /ingest/batch
```

### Request

**Content-Type**: `multipart/form-data`

**Form Data**:
- `files` (file[], required): Array of document files to upload

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/ingest/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.txt" \
  -F "files=@doc3.md"
```

**Example (JavaScript/Fetch)**:
```javascript
const formData = new FormData();
files.forEach(file => {
  formData.append('files', file);
});

fetch('http://localhost:5000/ingest/batch', {
  method: 'POST',
  body: formData
})
```

### Response

**Success (200 OK)**
```json
{
  "success": true,
  "processed": 2,
  "failed": 1,
  "results": [
    {
      "document_id": "doc_policy1.pdf_20",
      "chunks_created": 20,
      "filename": "policy1.pdf"
    },
    {
      "document_id": "doc_policy2.txt_10",
      "chunks_created": 10,
      "filename": "policy2.txt"
    }
  ],
  "errors": [
    {
      "filename": "corrupted.pdf",
      "error": "Failed to extract PDF: <error details>"
    }
  ]
}
```

**Error (400 Bad Request)**
```json
{
  "error": "No files provided"
}
```

---

## 4. Auto-Load Documents from Directory

Automatically load all documents from a specified directory.

### Endpoint
```
POST /ingest/auto
```

### Request

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "directory": "documents",  // Optional, defaults to configured DOCUMENTS_DIR
  "skip_existing": false      // Optional, defaults to false
}
```

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/ingest/auto \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "documents",
    "skip_existing": false
  }'
```

**Example (JavaScript/Fetch)**:
```javascript
fetch('http://localhost:5000/ingest/auto', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    directory: 'documents',
    skip_existing: false
  })
})
```

### Response

**Success (200 OK)**
```json
{
  "success": true,
  "processed": 3,
  "failed": 0,
  "total_files_found": 3,
  "results": [
    {
      "document_id": "doc_policy1.pdf_25",
      "chunks_created": 25,
      "filename": "policy1.pdf",
      "filepath": "documents/policy1.pdf"
    },
    {
      "document_id": "doc_policy2.txt_15",
      "chunks_created": 15,
      "filename": "policy2.txt",
      "filepath": "documents/policy2.txt"
    },
    {
      "document_id": "doc_policy3.pdf_30",
      "chunks_created": 30,
      "filename": "policy3.pdf",
      "filepath": "documents/policy3.pdf"
    }
  ],
  "errors": []
}
```

**No Files Found (200 OK)**
```json
{
  "success": true,
  "message": "No PDF/text files found in documents",
  "processed": 0,
  "failed": 0,
  "results": [],
  "errors": []
}
```

**Error (400 Bad Request)**
```json
{
  "error": "Directory does not exist: /invalid/path"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Auto-loading failed: <error message>"
}
```

---

## 5. List Available Documents

List all documents found in a directory.

### Endpoint
```
GET /ingest/list
```

### Request

**Query Parameters**:
- `directory` (string, optional): Directory path to scan. Defaults to configured DOCUMENTS_DIR.

**Example (cURL)**:
```bash
curl "http://localhost:5000/ingest/list?directory=documents"
```

**Example (JavaScript/Fetch)**:
```javascript
fetch('http://localhost:5000/ingest/list?directory=documents')
```

### Response

**Success (200 OK)**
```json
{
  "directory": "documents",
  "total_files": 3,
  "files": [
    {
      "filename": "policy1.pdf",
      "filepath": "documents/policy1.pdf",
      "size": 245678,
      "extension": ".pdf",
      "modified": "2024-01-15T10:20:30.123456"
    },
    {
      "filename": "policy2.txt",
      "filepath": "documents/policy2.txt",
      "size": 12345,
      "extension": ".txt",
      "modified": "2024-01-14T15:30:45.654321"
    },
    {
      "filename": "policy3.md",
      "filepath": "documents/policy3.md",
      "size": 8901,
      "extension": ".md",
      "modified": "2024-01-13T09:15:20.987654"
    }
  ]
}
```

**Error (400 Bad Request)**
```json
{
  "error": "Directory does not exist: /invalid/path"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Failed to list documents: <error message>"
}
```

---

## 6. Query the RAG System

Ask a question and get an AI-generated answer based on the policy documents. Optionally includes web search results for more comprehensive answers.

### Endpoint
```
POST /query
```

### Request

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "question": "What is Micro Center's return policy?",  // Required
  "top_k": 5,  // Optional, defaults to 5
  "use_web_search": false  // Optional, defaults to false. Set to true to include web search results
}
```

**Note**: Web search requires `ENABLE_WEB_SEARCH=true` to be set in environment variables. See `WEB_SEARCH_SETUP.md` for configuration details.

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Micro Center'\''s return policy?",
    "top_k": 5
  }'
```

**Example (JavaScript/Fetch)**:
```javascript
fetch('http://localhost:5000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: "What is Micro Center's return policy?",
    top_k: 5,
    use_web_search: false  // Set to true to enable web search
  })
})
```

**Example with Web Search**:
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Micro Center'\''s return policy?",
    "top_k": 5,
    "use_web_search": true
  }'
```

### Response

**Success (200 OK) - Without Web Search**
```json
{
  "question": "What is Micro Center's return policy?",
  "answer": "Based on Micro Center's policy documents, customers have 15 days from the date of purchase to return most items...\n\nSources:\n- policy1.pdf (chunk: policy1.pdf_chunk_0)\n- policy2.txt (chunk: policy2.txt_chunk_5)\n\n---\nℹ️ Policy Information: This information is based on Micro Center's current policies as documented. Policies may change, and specific situations may vary. For the most up-to-date information or questions about your specific order, please contact Micro Center customer service.",
  "citations": [
    "policy1.pdf (chunk: policy1.pdf_chunk_0)",
    "policy2.txt (chunk: policy2.txt_chunk_5)"
  ],
  "retrieved_chunks": [
    {
      "chunk_id": "policy1.pdf_chunk_0",
      "text": "Micro Center Return Policy: Customers have 15 days from the date of purchase to return most items in their original condition...",
      "source": "policy1.pdf",
      "page": "N/A",
      "score": 0.85
    },
    {
      "chunk_id": "policy2.txt_chunk_5",
      "text": "Return Process: To return an item, bring it to any Micro Center store location along with your receipt...",
      "source": "policy2.txt",
      "page": "N/A",
      "score": 0.78
    }
  ]
}
```

**Success (200 OK) - With Web Search**
```json
{
  "question": "What is Micro Center's return policy?",
  "answer": "Based on Micro Center's policy documents and current website information, customers have 15 days from the date of purchase to return most items...\n\nSources:\n- policy1.pdf (chunk: policy1.pdf_chunk_0)\n- https://www.microcenter.com/return-policy\n\n---\nℹ️ Policy Information: This information is based on Micro Center's current policies as documented. Policies may change, and specific situations may vary. For the most up-to-date information or questions about your specific order, please contact Micro Center customer service.",
  "citations": [
    "policy1.pdf (chunk: policy1.pdf_chunk_0)",
    "https://www.microcenter.com/return-policy"
  ],
  "retrieved_chunks": [
    {
      "chunk_id": "policy1.pdf_chunk_0",
      "text": "Micro Center Return Policy: Customers have 15 days from the date of purchase to return most items in their original condition...",
      "source": "policy1.pdf",
      "page": "N/A",
      "score": 0.85
    }
  ],
  "web_results": [
    {
      "title": "Return Policy - Micro Center",
      "snippet": "Micro Center offers a 15-day return policy for most items. Items must be in original condition with receipt...",
      "url": "https://www.microcenter.com/return-policy"
    },
    {
      "title": "Micro Center Return Policy Details",
      "snippet": "Customers can return items within 15 days of purchase. Electronics must be unopened...",
      "url": "https://www.microcenter.com/site/returns.aspx"
    }
  ]
}
```

**Error (400 Bad Request)**
```json
{
  "error": "Question is required"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Query failed: <error message>"
}
```

---

## 7. Web Search

Search the web for information. Can be used standalone or combined with local document retrieval.

### Endpoint
```
POST /search/web
```

### Request

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "query": "Micro Center return policy",  // Required
  "num_results": 5,  // Optional, defaults to 5
  "site_filter": "microcenter.com"  // Optional, filter results to specific domain
}
```

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/search/web \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Micro Center return policy",
    "num_results": 5,
    "site_filter": "microcenter.com"
  }'
```

**Example (JavaScript/Fetch)**:
```javascript
fetch('http://localhost:5000/search/web', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'Micro Center return policy',
    num_results: 5,
    site_filter: 'microcenter.com'
  })
})
```

### Response

**Success (200 OK)**
```json
{
  "query": "Micro Center return policy",
  "num_results": 3,
  "results": [
    {
      "title": "Return Policy - Micro Center",
      "snippet": "Micro Center offers a 15-day return policy for most items. Items must be in original condition with receipt and original packaging...",
      "url": "https://www.microcenter.com/return-policy",
      "source": "web_search"
    },
    {
      "title": "Micro Center Return Policy Details",
      "snippet": "Customers can return items within 15 days of purchase. Electronics must be unopened and in original packaging...",
      "url": "https://www.microcenter.com/site/returns.aspx",
      "source": "web_search"
    },
    {
      "title": "How to Return Items to Micro Center",
      "snippet": "To return an item, bring it to any Micro Center store location along with your receipt...",
      "url": "https://www.microcenter.com/help/returns",
      "source": "web_search"
    }
  ]
}
```

**Error (400 Bad Request) - Web Search Not Enabled**
```json
{
  "error": "Web search is not enabled. Set ENABLE_WEB_SEARCH=true and configure search API keys."
}
```

**Error (400 Bad Request)**
```json
{
  "error": "Query is required"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Web search failed: <error message>"
}
```

**Note**: Web search requires configuration. See `WEB_SEARCH_SETUP.md` for setup instructions.

---

## 8. Search Chunks (Retrieval Only)

Search for similar chunks without generating an answer. Useful for debugging retrieval.

### Endpoint
```
POST /search
```

### Request

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "query": "return policy",  // Required
  "top_k": 5  // Optional, defaults to 5
}
```

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "return policy",
    "top_k": 5
  }'
```

**Example (JavaScript/Fetch)**:
```javascript
fetch('http://localhost:5000/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'return policy',
    top_k: 5
  })
})
```

### Response

**Success (200 OK)**
```json
{
  "query": "return policy",
  "results": [
    {
      "chunk_id": "policy1.pdf_chunk_0",
      "text": "Micro Center Return Policy: Customers have 15 days from the date of purchase to return most items in their original condition with receipt. Items must be unopened and in original packaging...",
      "source": "policy1.pdf",
      "page": "N/A",
      "score": 0.92
    },
    {
      "chunk_id": "policy2.txt_chunk_3",
      "text": "Return Process: To return an item, bring it to any Micro Center store location along with your receipt. Refunds will be processed to the original payment method...",
      "source": "policy2.txt",
      "page": "N/A",
      "score": 0.85
    }
  ]
}
```

**Error (400 Bad Request)**
```json
{
  "error": "Query is required"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Search failed: <error message>"
}
```

---

## 9. Get Statistics

Get statistics about the vector database.

### Endpoint
```
GET /stats
```

### Request
No request body or parameters required.

**Example (cURL)**:
```bash
curl http://localhost:5000/stats
```

**Example (JavaScript/Fetch)**:
```javascript
fetch('http://localhost:5000/stats')
```

### Response

**Success (200 OK)**
```json
{
  "total_chunks": 150,
  "index_size": 150,
  "embedding_dimension": 384,
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Failed to get stats: <error message>"
}
```

---

## 10. Run Evaluation

Run evaluation on test questions to measure retrieval and faithfulness metrics.

### Endpoint
```
POST /evaluate
```

### Request

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "test_questions": [  // Optional, uses default if not provided
    {
      "question": "What is the return policy?",
      "expected_keywords": ["return", "policy", "refund"],
      "category": "returns"
    },
    {
      "question": "How long do I have to return an item?",
      "expected_keywords": ["return", "time", "days"],
      "category": "returns"
    }
  ]
}
```

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "test_questions": [
      {
        "question": "What is the return policy?",
        "expected_keywords": ["return", "policy"]
      }
    ]
  }'
```

**Example (JavaScript/Fetch)**:
```javascript
fetch('http://localhost:5000/evaluate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    test_questions: [
      {
        question: "What is the return policy?",
        expected_keywords: ["return", "policy"]
      }
    ]
  })
})
```

### Response

**Success (200 OK)**
```json
{
  "total_questions": 2,
  "retrieval_metrics": [
    {
      "question": "What is the return policy?",
      "metrics": {
        "num_retrieved": 5,
        "avg_score": 0.82,
        "recall_at_k": 0.75,
        "precision_at_k": 0.80
      }
    },
    {
      "question": "How long do I have to return an item?",
      "metrics": {
        "num_retrieved": 5,
        "avg_score": 0.78,
        "recall_at_k": 0.67,
        "precision_at_k": 0.60
      }
    }
  ],
  "faithfulness_scores": [
    {
      "question": "What is the return policy?",
      "answer": "Based on Micro Center's policy documents, customers have 15 days...",
      "faithfulness_score": 0.85
    },
    {
      "question": "How long do I have to return an item?",
      "answer": "According to the policy documents, the return period is 15 days...",
      "faithfulness_score": 0.78
    }
  ],
  "overall_metrics": {
    "average_precision_at_k": 0.70,
    "average_recall_at_k": 0.71,
    "average_similarity_score": 0.80,
    "average_faithfulness": 0.815,
    "total_evaluated": 2
  }
}
```

**Error (500 Internal Server Error)**
```json
{
  "error": "Evaluation failed: <error message>"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Error message describing what went wrong"
}
```

### 500 Internal Server Error
```json
{
  "error": "Error message describing the server error"
}
```

---

## TypeScript Interface Definitions

For TypeScript frontend development, here are the type definitions:

```typescript
// Health Check
interface HealthResponse {
  status: 'healthy';
  timestamp: string;
}

// Ingest Single Document
interface IngestResponse {
  success: boolean;
  document_id: string;
  chunks_created: number;
  filename: string;
}

// Ingest Batch
interface IngestBatchResponse {
  success: boolean;
  processed: number;
  failed: number;
  results: Array<{
    document_id: string;
    chunks_created: number;
    filename: string;
  }>;
  errors: Array<{
    filename: string;
    error: string;
  }>;
}

// Auto-Load
interface AutoLoadRequest {
  directory?: string;
  skip_existing?: boolean;
}

interface AutoLoadResponse {
  success: boolean;
  processed: number;
  failed: number;
  total_files_found: number;
  results: Array<{
    document_id: string;
    chunks_created: number;
    filename: string;
    filepath: string;
  }>;
  errors: Array<{
    filename: string;
    filepath: string;
    error: string;
  }>;
}

// List Documents
interface ListDocumentsResponse {
  directory: string;
  total_files: number;
  files: Array<{
    filename: string;
    filepath: string;
    size: number;
    extension: string;
    modified: string;
  }>;
}

// Query
interface QueryRequest {
  question: string;
  top_k?: number;
  use_web_search?: boolean;  // Optional, enable web search
}

interface QueryResponse {
  question: string;
  answer: string;
  citations: string[];
  retrieved_chunks: Array<{
    chunk_id: string;
    text: string;
    source: string;
    page: string;
    score: number;
  }>;
  web_results?: Array<{  // Present when use_web_search is true
    title: string;
    snippet: string;
    url: string;
  }>;
}

// Search (Local Chunks)
interface SearchRequest {
  query: string;
  top_k?: number;
}

interface SearchResponse {
  query: string;
  results: Array<{
    chunk_id: string;
    text: string;
    source: string;
    page: string;
    score: number;
  }>;
}

// Web Search
interface WebSearchRequest {
  query: string;
  num_results?: number;
  site_filter?: string;
}

interface WebSearchResponse {
  query: string;
  num_results: number;
  results: Array<{
    title: string;
    snippet: string;
    url: string;
    source: string;
  }>;
}

// Stats
interface StatsResponse {
  total_chunks: number;
  index_size: number;
  embedding_dimension: number;
  model: string;
}

// Evaluate
interface TestQuestion {
  question: string;
  expected_keywords?: string[];
  category?: string;
}

interface EvaluateRequest {
  test_questions?: TestQuestion[];
}

interface EvaluateResponse {
  total_questions: number;
  retrieval_metrics: Array<{
    question: string;
    metrics: {
      num_retrieved: number;
      avg_score: number;
      recall_at_k: number;
      precision_at_k: number;
    };
  }>;
  faithfulness_scores: Array<{
    question: string;
    answer?: string;
    error?: string;
    faithfulness_score: number;
  }>;
  overall_metrics: {
    average_precision_at_k: number;
    average_recall_at_k: number;
    average_similarity_score: number;
    average_faithfulness: number;
    total_evaluated: number;
  };
}

// Error Response
interface ErrorResponse {
  error: string;
}
```

---

## Notes

1. **CORS**: The API has CORS enabled, so it can be accessed from frontend applications running on different origins.

2. **File Upload Limits**: Flask's default file upload size limit applies. For large files, you may need to configure `MAX_CONTENT_LENGTH` in Flask.

3. **Supported File Types**: PDF (.pdf), Text (.txt), and Markdown (.md) files are supported.

4. **Base URL**: All endpoints are relative to the base URL (default: `http://localhost:5000`).

5. **Content-Type**: 
   - Use `multipart/form-data` for file uploads (`/ingest`, `/ingest/batch`)
   - Use `application/json` for all other POST requests

6. **Error Handling**: Always check the HTTP status code. A 200 status doesn't guarantee success - check for `error` fields in the response.

7. **Web Search**: 
   - Web search is optional and requires configuration (see `WEB_SEARCH_SETUP.md`)
   - Supported providers: DuckDuckGo (no API key), Google Custom Search, Bing
   - Use `use_web_search: true` in `/query` to combine local and web results
   - Use `/search/web` for web-only searches
   - Site filtering helps ensure results from specific domains (e.g., `microcenter.com`)

