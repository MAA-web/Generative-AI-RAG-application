# Quick Start Guide

## 1. Install Dependencies

```bash
cd RAG-backend
pip install -r requirements.txt
```

## 2. Set Up LLM API Key (Optional but Recommended)

For Gemini API:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
# Or use LLM_API_KEY for backward compatibility
export LLM_API_KEY="your-gemini-api-key"
export LLM_PROVIDER="gemini"  # Optional, defaults to gemini
```

For OpenAI:
```bash
export LLM_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"
```

**Note**: If no API key is set, the system will still work but provide basic retrieval-only responses.

## 3. Start the Server

```bash
python main.py
```

You should see:
```
Starting RAG Backend Server...
Upload folder: documents
Vector DB path: vector_db
Embeddings model: sentence-transformers/all-MiniLM-L6-v2
LLM Provider: gemini
LLM API Key: Set (or Not set)
...
Server starting on http://0.0.0.0:5000
```

## 4. Ingest Your PDF Documents

In a new terminal:

```bash
# Single document
curl -X POST http://localhost:5000/ingest \
  -F "file=@path/to/your/document.pdf"

# Multiple documents
curl -X POST http://localhost:5000/ingest/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```

## 5. Query the System

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the vaccination guidelines?",
    "top_k": 5
  }'
```

## 6. Run Evaluation

```bash
curl -X POST http://localhost:5000/evaluate
```

## Example Python Usage

```python
import requests

# Query
response = requests.post("http://localhost:5000/query", json={
    "question": "How can I prevent common illnesses?",
    "top_k": 5
})
print(response.json())
```

## Troubleshooting

### "sentence-transformers not available"
```bash
pip install sentence-transformers
```

### "FAISS not available"
```bash
pip install faiss-cpu
# Or for GPU: pip install faiss-gpu
```

### PDF processing fails
```bash
pip install pdfplumber PyPDF2
```

### First run is slow
The first time you run the server, it will download the embeddings model (~80MB). This is normal and only happens once.

## Next Steps

1. Add your Micro Center policy documents (PDFs/text files) to the system
2. Test with various questions
3. Review the evaluation metrics
4. Customize chunk size and overlap if needed
5. Adjust scope keywords for your use case

