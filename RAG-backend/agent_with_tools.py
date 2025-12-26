"""
Agent with function calling capabilities using OpenAI/Anthropic function calling.
This implements proper tool integration for the customer service agent.
"""

import json
from typing import Dict, List, Any, Optional
from customer_service_tools import CustomerServiceTools
from llm_client import LLMClient

class AgentWithTools:
    """
    Customer service agent with function calling capabilities.
    Uses LLM function calling to autonomously select and execute tools.
    """
    
    def __init__(self, tools: CustomerServiceTools, llm_client: LLMClient):
        """
        Initialize agent with tools.
        
        Args:
            tools: CustomerServiceTools instance
            llm_client: LLM client for function calling
        """
        self.tools = tools
        self.llm_client = llm_client
        self.tool_functions = {
            'get_order_by_id': tools.get_order_by_id,
            'get_orders_by_customer': tools.get_orders_by_customer,
            'search_policies': tools.search_policies,
            'update_order_status': tools.update_order_status,
            'create_support_ticket': tools.create_support_ticket,
            'search_orders': tools.search_orders,
        }
    
    def process_query_with_tools(self, query: str, customer_id: Optional[str] = None, 
                                 max_iterations: int = 5) -> Dict[str, Any]:
        """
        Process customer query using function calling to autonomously select tools.
        
        Args:
            query: Customer query
            customer_id: Optional customer ID for context
            max_iterations: Maximum number of tool calls (to prevent infinite loops)
            
        Returns:
            Dictionary with answer and tool execution history
        """
        # Add customer context to query if provided
        if customer_id:
            query = f"Customer ID: {customer_id}. {query}"
        
        conversation_history = []
        tool_calls_history = []
        
        current_query = query
        
        for iteration in range(max_iterations):
            # Get function definitions
            functions = self.tools.get_function_definitions()
            
            # Call LLM with function calling
            if self.llm_client.provider in ['openai', 'anthropic']:
                # Use function calling API
                response = self._call_with_function_calling(
                    query=current_query,
                    functions=functions,
                    conversation_history=conversation_history
                )
            else:
                # For Gemini or other providers, use structured prompting
                response = self._call_with_structured_prompt(
                    query=current_query,
                    functions=functions,
                    conversation_history=conversation_history
                )
            
            # Check if LLM wants to call a function
            if 'function_call' in response or 'tool_calls' in response:
                # Extract function call
                function_call = response.get('function_call') or (response.get('tool_calls', [{}])[0] if response.get('tool_calls') else {})
                
                if function_call:
                    function_name = function_call.get('name') or function_call.get('function', {}).get('name')
                    function_args = function_call.get('arguments') or function_call.get('function', {}).get('arguments')
                    
                    if isinstance(function_args, str):
                        function_args = json.loads(function_args)
                    
                    # Execute tool
                    if function_name in self.tool_functions:
                        tool_result = self.tool_functions[function_name](**function_args)
                        tool_calls_history.append({
                            'tool': function_name,
                            'arguments': function_args,
                            'result': tool_result
                        })
                        
                        # Add to conversation history
                        conversation_history.append({
                            'role': 'assistant',
                            'content': f"I called {function_name} with {function_args}"
                        })
                        conversation_history.append({
                            'role': 'function',
                            'name': function_name,
                            'content': tool_result
                        })
                        
                        # Continue loop to let LLM process tool result
                        current_query = f"Tool result: {tool_result}. Continue processing the customer query: {query}"
                    else:
                        # Unknown function, break and generate final answer
                        break
                else:
                    # No function call, generate final answer
                    break
            else:
                # No function call needed, return answer
                final_answer = response.get('content') or response.get('text', '')
                return {
                    'answer': final_answer,
                    'tool_calls': tool_calls_history,
                    'iterations': iteration + 1
                }
        
        # If we've exhausted iterations, generate final answer with all tool results
        final_context = self._build_context_from_tool_results(tool_calls_history)
        final_answer = self.llm_client.generate(
            prompt=f"Based on the following information, answer the customer's question: {query}",
            context=final_context,
            template='balanced'
        )
        
        return {
            'answer': final_answer,
            'tool_calls': tool_calls_history,
            'iterations': len(tool_calls_history)
        }
    
    def _call_with_function_calling(self, query: str, functions: List[Dict], 
                                    conversation_history: List[Dict]) -> Dict:
        """
        Call LLM with function calling (OpenAI/Anthropic).
        
        This is a placeholder - actual implementation depends on provider.
        """
        # This would use the actual function calling API
        # For now, return a structured response
        return {
            'content': 'Function calling not fully implemented for this provider',
            'function_call': None
        }
    
    def _call_with_structured_prompt(self, query: str, functions: List[Dict],
                                     conversation_history: List[Dict]) -> Dict:
        """
        Call LLM with structured prompt (for providers without function calling).
        
        Uses prompt engineering to simulate function calling.
        """
        # Build prompt with available functions
        functions_text = "\n".join([
            f"- {f['function']['name']}: {f['function']['description']}"
            for f in functions
        ])
        
        prompt = f"""You are a customer service agent with access to the following tools:

{functions_text}

Customer Query: {query}

Available Tools:
{json.dumps([f['function']['name'] for f in functions], indent=2)}

Based on the query, decide if you need to call a tool. If yes, respond in this JSON format:
{{
    "function_call": {{
        "name": "tool_name",
        "arguments": {{"arg1": "value1"}}
    }}
}}

If no tool is needed, respond with your answer directly.
"""
        
        response = self.llm_client.generate(prompt=prompt, context="", template='balanced')
        
        # Try to parse function call from response
        try:
            if 'function_call' in response or '{' in response:
                # Try to extract JSON
                import re
                json_match = re.search(r'\{[^}]+\}', response)
                if json_match:
                    parsed = json.loads(json_match.group())
                    if 'function_call' in parsed:
                        return {'function_call': parsed['function_call']}
        except:
            pass
        
        return {'content': response, 'function_call': None}
    
    def _build_context_from_tool_results(self, tool_calls: List[Dict]) -> str:
        """Build context string from tool execution results."""
        context_parts = []
        for call in tool_calls:
            context_parts.append(
                f"Tool: {call['tool']}\n"
                f"Arguments: {json.dumps(call['arguments'])}\n"
                f"Result: {call['result']}\n"
            )
        return "\n---\n".join(context_parts)

