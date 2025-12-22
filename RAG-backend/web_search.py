"""
Web search module for online information retrieval.

This module provides web search functionality to supplement local document
retrieval. Supports multiple search providers:
- DuckDuckGo: Free, no API key required (uses HTML scraping)
- Google Custom Search: Requires API key and search engine ID
- Bing Web Search: Requires Azure API key

The search results are formatted for inclusion in LLM context, allowing
the RAG system to combine local documents with up-to-date web information.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote


class WebSearch:
    """Web search client for retrieving online information."""
    
    def __init__(self, provider: str = 'duckduckgo', api_key: Optional[str] = None, 
                 search_engine_id: Optional[str] = None):
        """
        Initialize web search client.
        
        Args:
            provider: Search provider ('google', 'duckduckgo', 'bing')
            api_key: API key for the search provider
            search_engine_id: Search engine ID (for Google Custom Search)
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv('SEARCH_API_KEY')
        self.search_engine_id = search_engine_id or os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    def search(self, query: str, num_results: int = 5, site_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            num_results: Number of results to return
            site_filter: Optional site filter (e.g., 'microcenter.com')
            
        Returns:
            List of search results with title, snippet, and URL
        """
        if self.provider == 'google':
            return self._search_google(query, num_results, site_filter)
        elif self.provider == 'bing':
            return self._search_bing(query, num_results, site_filter)
        else:
            return self._search_duckduckgo(query, num_results, site_filter)
    
    def _search_google(self, query: str, num_results: int, site_filter: Optional[str]) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google Custom Search requires SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID")
        
        # Add site filter if provided
        if site_filter:
            query = f"site:{site_filter} {query}"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10)  # Google API max is 10 per request
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('items', [])[:num_results]:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': 'web_search'
                })
            
            return results
        except Exception as e:
            print(f"Google search failed: {e}")
            return []
    
    def _search_bing(self, query: str, num_results: int, site_filter: Optional[str]) -> List[Dict[str, Any]]:
        """Search using Bing Web Search API."""
        if not self.api_key:
            raise ValueError("Bing Search requires SEARCH_API_KEY")
        
        # Add site filter if provided
        if site_filter:
            query = f"site:{site_filter} {query}"
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        params = {
            'q': query,
            'count': min(num_results, 50),
            'textDecorations': False,
            'textFormat': 'Raw'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('webPages', {}).get('value', [])[:num_results]:
                results.append({
                    'title': item.get('name', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('url', ''),
                    'source': 'web_search'
                })
            
            return results
        except Exception as e:
            print(f"Bing search failed: {e}")
            return []
    
    def _search_duckduckgo(self, query: str, num_results: int, site_filter: Optional[str]) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo HTML API (no API key required).
        
        Uses DuckDuckGo's HTML interface and parses results. This is a free
        option but may be less reliable than API-based providers. Includes
        fallback parsing if BeautifulSoup is not available.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            site_filter: Optional domain filter (e.g., 'microcenter.com')
            
        Returns:
            List of search results with title, snippet, and URL
            
        Note:
            Requires HTML parsing which can break if DuckDuckGo changes their
            page structure. For production, consider using Google/Bing APIs.
        """
        try:
            # Use DuckDuckGo HTML API (no API key needed, but requires HTML parsing)
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query
            }
            
            # Add site filter if provided
            if site_filter:
                params['q'] = f"site:{site_filter} {query}"
            
            # Use browser-like User-Agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML results - try BeautifulSoup first (better parsing)
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
            except ImportError:
                # Fallback: simple regex-based parsing if BeautifulSoup not available
                import re
                # Extract basic information from HTML using regex patterns
                title_pattern = r'<a[^>]*class="result__a"[^>]*>([^<]+)</a>'
                url_pattern = r'href="([^"]+)"'
                titles = re.findall(title_pattern, response.text)
                urls = re.findall(url_pattern, response.text)
                
                # Match titles with URLs (simple approach - may have mismatches)
                results = []
                for i, (title, url) in enumerate(zip(titles[:num_results], urls[:num_results])):
                    results.append({
                        'title': title.strip(),
                        'snippet': '',  # Regex parsing doesn't extract snippets easily
                        'url': url,
                        'source': 'web_search'
                    })
                return results
            
            # Parse results using BeautifulSoup (more reliable)
            results = []
            result_divs = soup.find_all('div', class_='result')[:num_results]
            
            for div in result_divs:
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'url': title_elem.get('href', ''),
                        'source': 'web_search'
                    })
            
            return results
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            # Return empty results on failure (don't crash the system)
            return []
    
    def format_search_results_as_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format web search results as context string for LLM.
        
        Converts search results into a formatted string that can be included
        in the LLM prompt alongside document chunks. Each result includes
        title, URL, and snippet for citation purposes.
        
        Args:
            results: List of search result dictionaries with title, snippet, url
            
        Returns:
            Formatted context string with web results, or empty string if no results
            
        Example Output:
            "[Web Result 1: Title]\nURL: https://...\nContent: snippet...\n\n---\n..."
        """
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            # Format each result with title, URL, and content snippet
            context_parts.append(
                f"[Web Result {i}: {result.get('title', 'Unknown')}]\n"
                f"URL: {result.get('url', '')}\n"
                f"Content: {result.get('snippet', '')}\n"
            )
        
        # Join results with separator for clarity
        return "\n---\n".join(context_parts)

