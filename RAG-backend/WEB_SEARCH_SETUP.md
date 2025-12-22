# Web Search Integration Guide

This guide explains how to enable and configure web search functionality in the RAG system.

## Overview

The web search feature allows the RAG system to:
1. Search the web for additional information
2. Combine local document retrieval with web search results
3. Provide more comprehensive answers using both sources

## Supported Search Providers

### 1. DuckDuckGo (Default, No API Key Required)
- **Provider**: `duckduckgo`
- **API Key**: Not required
- **Pros**: Free, no setup needed
- **Cons**: Limited customization, may have rate limits

### 2. Google Custom Search
- **Provider**: `google`
- **API Key**: Required (`SEARCH_API_KEY`)
- **Search Engine ID**: Required (`GOOGLE_SEARCH_ENGINE_ID`)
- **Setup**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create a project and enable Custom Search API
  3. Create a Custom Search Engine at [Google Programmable Search](https://programmablesearchengine.google.com/)
  4. Get your API key and Search Engine ID
- **Pros**: High quality results, reliable
- **Cons**: Requires API key, has usage limits

### 3. Bing Web Search API
- **Provider**: `bing`
- **API Key**: Required (`SEARCH_API_KEY`)
- **Setup**:
  1. Go to [Azure Portal](https://portal.azure.com/)
  2. Create a Bing Search v7 resource
  3. Get your subscription key
- **Pros**: Good quality results
- **Cons**: Requires Azure account, API key

## Configuration

### Environment Variables

Add these to your `.env` file or set as environment variables:

```bash
# Enable web search
ENABLE_WEB_SEARCH=true

# Choose provider: 'duckduckgo', 'google', or 'bing'
WEB_SEARCH_PROVIDER=duckduckgo

# API keys (only required for Google/Bing)
SEARCH_API_KEY=your-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id  # Only for Google
```

### Quick Start (DuckDuckGo - No API Key)

```bash
export ENABLE_WEB_SEARCH=true
export WEB_SEARCH_PROVIDER=duckduckgo
python main.py
```

### Google Custom Search Setup

```bash
export ENABLE_WEB_SEARCH=true
export WEB_SEARCH_PROVIDER=google
export SEARCH_API_KEY=your-google-api-key
export GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
python main.py
```

### Bing Search Setup

```bash
export ENABLE_WEB_SEARCH=true
export WEB_SEARCH_PROVIDER=bing
export SEARCH_API_KEY=your-bing-subscription-key
python main.py
```

## API Usage

### 1. Query with Web Search

Enable web search for a specific query:

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Micro Center'\''s return policy?",
    "top_k": 5,
    "use_web_search": true
  }'
```

**Response includes web results:**
```json
{
  "question": "What is Micro Center's return policy?",
  "answer": "...",
  "citations": [...],
  "retrieved_chunks": [...],
  "web_results": [
    {
      "title": "Micro Center Return Policy - Official Site",
      "snippet": "Micro Center offers a 15-day return policy...",
      "url": "https://www.microcenter.com/return-policy"
    }
  ]
}
```

### 2. Web Search Only

Search the web without using local documents:

```bash
curl -X POST http://localhost:5000/search/web \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Micro Center return policy",
    "num_results": 5,
    "site_filter": "microcenter.com"
  }'
```

**Response:**
```json
{
  "query": "Micro Center return policy",
  "num_results": 5,
  "results": [
    {
      "title": "Return Policy - Micro Center",
      "snippet": "Customers have 15 days from purchase date...",
      "url": "https://www.microcenter.com/return-policy",
      "source": "web_search"
    }
  ]
}
```

## How It Works

### Hybrid Retrieval

When `use_web_search: true` is set:

1. **Local Retrieval**: System retrieves relevant chunks from your vector database
2. **Web Search**: System searches the web (optionally filtered to specific sites)
3. **Context Combination**: Both local and web results are combined into context
4. **Answer Generation**: LLM generates answer using combined context
5. **Citations**: Both local document citations and web URLs are included

### Site Filtering

You can filter web search results to specific domains:

```json
{
  "query": "return policy",
  "site_filter": "microcenter.com"
}
```

This ensures results are from Micro Center's official website.

## Frontend Integration

### TypeScript Example

```typescript
interface QueryRequest {
  question: string;
  top_k?: number;
  use_web_search?: boolean;
}

interface QueryResponse {
  question: string;
  answer: string;
  citations: string[];
  retrieved_chunks: Array<{
    chunk_id: string;
    text: string;
    source: string;
    score: number;
  }>;
  web_results?: Array<{
    title: string;
    snippet: string;
    url: string;
  }>;
}

// Query with web search
const queryWithWebSearch = async (question: string) => {
  const response = await fetch('http://localhost:5000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question,
      top_k: 5,
      use_web_search: true
    })
  });
  
  return await response.json() as QueryResponse;
};
```

## Best Practices

1. **Use Web Search Selectively**: Enable web search only when:
   - Local documents don't have enough information
   - You need up-to-date information
   - User explicitly requests web search

2. **Site Filtering**: Always filter to official domains when possible to ensure accuracy

3. **Rate Limiting**: Be aware of API rate limits, especially with Google/Bing

4. **Cost Management**: Google and Bing APIs have usage costs - monitor usage

5. **Fallback**: Always have a fallback when web search fails

## Troubleshooting

### Web Search Not Working

1. **Check if enabled**: Verify `ENABLE_WEB_SEARCH=true`
2. **Check provider**: Ensure `WEB_SEARCH_PROVIDER` is set correctly
3. **Check API keys**: For Google/Bing, verify API keys are valid
4. **Check logs**: Look for error messages in server logs

### DuckDuckGo Issues

- DuckDuckGo may have rate limits
- HTML parsing may fail if page structure changes
- Consider using Google/Bing for production

### Google Custom Search Issues

- Verify API key has Custom Search API enabled
- Check Search Engine ID is correct
- Ensure billing is enabled in Google Cloud Console

### Bing Search Issues

- Verify subscription key is correct
- Check Azure resource is active
- Ensure correct API endpoint is used

## Example Use Cases

### 1. Policy Updates
Use web search to get the latest policy information:
```json
{
  "question": "What is the current return policy?",
  "use_web_search": true,
  "site_filter": "microcenter.com"
}
```

### 2. Product Information
Search for product-specific information:
```json
{
  "question": "What is Micro Center's warranty policy for laptops?",
  "use_web_search": true
}
```

### 3. Store Locations
Find store-specific information:
```json
{
  "query": "Micro Center store hours",
  "site_filter": "microcenter.com"
}
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Input Validation**: Validate and sanitize search queries
4. **Error Handling**: Don't expose API keys in error messages

