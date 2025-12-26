"""
LLM client for making API calls to language models.

This module provides a unified interface for calling different LLM providers:
- Google Gemini (via SDK or HTTP API)
- OpenAI (via HTTP API)
- Anthropic Claude (via HTTP API)

The client builds RAG-specific prompts that instruct the LLM to answer based
only on provided context, with citations and safety considerations.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional

# Try to import Google GenAI SDK (preferred method for Gemini)
try:
    from google import genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GEMINI_SDK_AVAILABLE = False
    print("Warning: google-genai not available. Install with: pip install google-genai")


class LLMClient:
    """Client for calling LLM APIs using SDKs (Gemini) or HTTP requests (OpenAI, Anthropic)."""
    
    def __init__(self, provider: str = 'gemini', api_key: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider ('gemini', 'openai', 'anthropic')
            api_key: API key for the provider
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv('LLM_API_KEY') or os.getenv('GEMINI_API_KEY')
        
        # Initialize Gemini client if available
        if self.provider == 'gemini' and GEMINI_SDK_AVAILABLE:
            # Set API key in environment if provided and not already set
            if self.api_key and not os.getenv('GEMINI_API_KEY'):
                os.environ['GEMINI_API_KEY'] = self.api_key
            try:
                self.gemini_client = genai.Client()
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
                self.gemini_client = None
        else:
            self.gemini_client = None
        
        if not self.api_key and self.provider == 'gemini':
            print(f"Warning: No API key provided for {provider}. Set LLM_API_KEY or GEMINI_API_KEY environment variable.")
    
    def generate(self, prompt: str, context: Optional[str] = None, max_tokens: int = 512, 
                 template: str = 'balanced') -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User question/prompt
            context: Retrieved context to include
            max_tokens: Maximum tokens to generate
            template: Prompt template to use ('strict', 'balanced', 'permissive')
            
        Returns:
            Generated text response
        """
        if self.provider == 'gemini':
            return self._call_gemini(prompt, context, max_tokens, template)
        elif self.provider == 'openai':
            return self._call_openai(prompt, context, max_tokens, template)
        elif self.provider == 'anthropic':
            return self._call_anthropic(prompt, context, max_tokens, template)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _call_gemini(self, prompt: str, context: Optional[str], max_tokens: int, template: str = 'balanced') -> str:
        """
        Call Google Gemini API using the SDK (preferred) or HTTP API (fallback).
        
        Args:
            prompt: User question
            context: Retrieved context from documents
            max_tokens: Maximum tokens to generate (currently not used with SDK)
            template: Prompt template to use ('strict', 'balanced', 'permissive')
            
        Returns:
            Generated text response from Gemini
            
        Note:
            Prefers SDK method (google-genai) but falls back to HTTP API if SDK
            is not available. The SDK method is simpler and more reliable.
        """
        # Build RAG-specific prompt with context
        full_prompt = self._build_rag_prompt(prompt, context, template)
        
        # Try SDK method first (preferred - simpler and more reliable)
        if GEMINI_SDK_AVAILABLE and self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",  # Using latest flash model
                    contents=full_prompt
                )
                return response.text
            except Exception as e:
                raise ValueError(f"Gemini API call failed: {str(e)}")
        
        # Fallback to HTTP API if SDK not available
        if not self.api_key:
            return self._fallback_response(prompt, context)
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract text from Gemini response
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0].get('content', {})
                parts = content.get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text']
            
            raise ValueError("Unexpected response format from Gemini API")
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Gemini API call failed: {str(e)}")
    
    def _call_openai(self, prompt: str, context: Optional[str], max_tokens: int, template: str = 'balanced') -> str:
        """Call OpenAI API."""
        if not self.api_key:
            return self._fallback_response(prompt, context)
        
        url = "https://api.openai.com/v1/chat/completions"
        
        full_prompt = self._build_rag_prompt(prompt, context, template)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            
            raise ValueError("Unexpected response format from OpenAI API")
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"OpenAI API call failed: {str(e)}")
    
    def _call_anthropic(self, prompt: str, context: Optional[str], max_tokens: int, template: str = 'balanced') -> str:
        """Call Anthropic Claude API."""
        if not self.api_key:
            return self._fallback_response(prompt, context)
        
        url = "https://api.anthropic.com/v1/messages"
        
        full_prompt = self._build_rag_prompt(prompt, context, template)
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'content' in result and len(result['content']) > 0:
                return result['content'][0]['text']
            
            raise ValueError("Unexpected response format from Anthropic API")
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Anthropic API call failed: {str(e)}")
    
    def _build_rag_prompt(self, question: str, context: Optional[str], template: str = 'balanced') -> str:
        """
        Build RAG-specific prompt for LLM generation.
        
        Constructs a prompt that instructs the LLM to:
        - Answer only from provided context (no external knowledge)
        - Include citations
        - Be customer-friendly and accurate
        - Redirect out-of-scope questions appropriately
        
        Args:
            question: User's question
            context: Retrieved context from documents (and optionally web search)
            template: Prompt template to use ('strict', 'balanced', 'permissive')
                - 'strict': Maximum faithfulness, explicit anti-hallucination warnings
                - 'balanced': Moderate approach (default)
                - 'permissive': Allows some general knowledge but emphasizes context
            
        Returns:
            Formatted prompt string ready for LLM API call
        """
        if context:
            if template == 'strict':
                # Template 1: STRICT - Maximum faithfulness, explicit anti-hallucination
                prompt = f"""You are a customer service assistant for Micro Center. CRITICAL: You must ONLY use information from the provided context. DO NOT use any external knowledge, assumptions, or information not explicitly stated in the context.

ANTI-HALLUCINATION RULES:
- If information is not in the context, you MUST say "I don't have that information in the policy documents"
- DO NOT infer, assume, or guess any details not explicitly stated
- DO NOT add information from your training data
- If the context is unclear or incomplete, explicitly state this limitation

Context from policy documents:
{context}

Question: {question}

REQUIRED RESPONSE FORMAT:
1. Answer ONLY using information directly from the context above
2. If the answer is not in the context, respond: "I don't have specific information about this in the policy documents. Please contact Micro Center customer service for assistance."
3. Include exact citations: [Source: document_name]
4. Do not paraphrase in ways that add information not in the context
5. If you're uncertain, state your uncertainty clearly

Answer:"""
            
            elif template == 'permissive':
                # Template 3: PERMISSIVE - Allows some general knowledge but emphasizes context
                prompt = f"""You are a helpful customer service assistant for Micro Center, an electronics and computer retailer. Answer the user's question primarily using the provided context, but you may supplement with general knowledge about retail policies if the context doesn't fully address the question.

Context from policy documents:
{context}

Question: {question}

Instructions:
1. Prioritize information from the provided context above all else
2. If the context provides partial information, you may use general retail knowledge to provide a more complete answer, but clearly distinguish between what's from the documents vs. general knowledge
3. If the context doesn't contain relevant information, you may provide general guidance but always suggest contacting customer service for specific details
4. Include citations for information from the context (e.g., [Source: document_name])
5. Be helpful, accurate, and customer-friendly
6. Focus on policies related to returns, exchanges, warranties, shipping, refunds, and store information

Answer:"""
            
            else:
                # Template 2: BALANCED - Moderate approach (default)
                prompt = f"""You are a helpful customer service assistant for Micro Center, an electronics and computer retailer. Answer the user's question using ONLY the provided context from Micro Center's policy documents. Do not use any external knowledge.

Context from policy documents:
{context}

Question: {question}

Instructions:
1. Answer the question based ONLY on the provided context from Micro Center's policies
2. If the context doesn't contain enough information, say so clearly and suggest contacting customer service
3. Include citations in your answer (e.g., [Source: document_name])
4. Be concise, accurate, and customer-friendly
5. Focus on policies related to returns, exchanges, warranties, shipping, refunds, and store information
6. If asked about something not covered in the policies, politely direct them to contact Micro Center customer service

Answer:"""
        else:
            # Prompt without context - fallback when no documents are available
            prompt = f"""You are a helpful customer service assistant for Micro Center. Answer the user's question about Micro Center's policies.

Question: {question}

Note: If you don't have enough information to answer, suggest contacting Micro Center customer service for assistance.

Answer:"""
        
        return prompt
    
    def _fallback_response(self, prompt: str, context: Optional[str]) -> str:
        """Fallback response when API key is not available."""
        if context:
            return f"Based on the provided context, here is relevant information:\n\n{context[:500]}...\n\nNote: LLM API key not configured. This is a basic retrieval-only response. Please set LLM_API_KEY environment variable for full answer generation."
        else:
            return "I apologize, but the LLM API is not configured. Please set the LLM_API_KEY environment variable to enable answer generation."

