"""
Example usage script for the RAG backend system.
Demonstrates how to use the API endpoints programmatically.
"""

import requests
import json
import os

BASE_URL = "http://localhost:5000"

def health_check():
    """Check if the server is running."""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())
    return response.status_code == 200

def ingest_document(filepath):
    """Ingest a document."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/ingest", files=files)
    
    result = response.json()
    print(f"Ingestion Result: {json.dumps(result, indent=2)}")
    return result

def query(question, top_k=5):
    """Query the RAG system."""
    data = {
        "question": question,
        "top_k": top_k
    }
    response = requests.post(f"{BASE_URL}/query", json=data)
    result = response.json()
    print(f"\nQuestion: {question}")
    print(f"Answer: {result.get('answer', 'No answer')}")
    print(f"Citations: {result.get('citations', [])}")
    return result

def search(query_text, top_k=5):
    """Search for similar chunks."""
    data = {
        "query": query_text,
        "top_k": top_k
    }
    response = requests.post(f"{BASE_URL}/search", json=data)
    result = response.json()
    print(f"\nSearch Query: {query_text}")
    print(f"Found {len(result.get('results', []))} results")
    for i, res in enumerate(result.get('results', [])[:3], 1):
        print(f"\nResult {i}:")
        print(f"  Source: {res.get('source')}")
        print(f"  Score: {res.get('score', 0):.4f}")
        print(f"  Text: {res.get('text', '')[:200]}...")
    return result

def get_stats():
    """Get system statistics."""
    response = requests.get(f"{BASE_URL}/stats")
    result = response.json()
    print("\nSystem Statistics:")
    print(json.dumps(result, indent=2))
    return result

def evaluate():
    """Run evaluation."""
    response = requests.post(f"{BASE_URL}/evaluate")
    result = response.json()
    print("\nEvaluation Results:")
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    print("RAG Backend Example Usage")
    print("=" * 50)
    
    # Check if server is running
    if not health_check():
        print("Server is not running. Please start it with: python main.py")
        exit(1)
    
    # Example workflow
    print("\n1. Getting system statistics...")
    get_stats()
    
    print("\n2. Example query (without documents)...")
    query("What are vaccination guidelines?")
    
    print("\n3. Example search...")
    search("prevention guidelines")
    
    print("\n" + "=" * 50)
    print("To ingest documents, use:")
    print("  ingest_document('path/to/document.pdf')")
    print("\nTo run evaluation, use:")
    print("  evaluate()")

