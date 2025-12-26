"""
Customer Service Tools for LangChain integration.
Defines tools that can be used by an agent with function calling.
"""

from typing import Dict, Any, Optional, List
from order_database import OrderDatabase
from rag_pipeline import RAGPipeline
import json

class CustomerServiceTools:
    """Collection of tools for customer service agent."""
    
    def __init__(self, order_db: OrderDatabase, rag_pipeline: RAGPipeline):
        """
        Initialize customer service tools.
        
        Args:
            order_db: Order database instance
            rag_pipeline: RAG pipeline for policy retrieval
        """
        self.order_db = order_db
        self.rag_pipeline = rag_pipeline
    
    def get_order_by_id(self, order_id: str) -> str:
        """
        Tool: Get order information by order ID.
        
        Args:
            order_id: Order identifier (e.g., "ORD001")
            
        Returns:
            JSON string with order information or error message
        """
        order = self.order_db.get_order_by_id(order_id)
        if order:
            context = self.order_db.format_order_context(order)
            return json.dumps({
                'success': True,
                'order': order,
                'formatted_context': context
            }, default=str)
        return json.dumps({
            'success': False,
            'error': f'Order {order_id} not found'
        })
    
    def get_orders_by_customer(self, customer_id: str) -> str:
        """
        Tool: Get all orders for a customer.
        
        Args:
            customer_id: Customer identifier (e.g., "CUST001")
            
        Returns:
            JSON string with list of orders
        """
        orders = self.order_db.get_orders_by_customer(customer_id)
        return json.dumps({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }, default=str)
    
    def search_policies(self, query: str, top_k: int = 5) -> str:
        """
        Tool: Search policy documents for relevant information.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            JSON string with retrieved policy chunks
        """
        chunks = self.rag_pipeline.retrieve(query, top_k=top_k)
        results = []
        for chunk in chunks:
            results.append({
                'text': chunk.get('text', ''),
                'source': chunk.get('metadata', {}).get('source', 'Unknown'),
                'score': chunk.get('score', 0.0)
            })
        return json.dumps({
            'success': True,
            'results': results,
            'count': len(results)
        }, default=str)
    
    def update_order_status(self, order_id: str, status: str) -> str:
        """
        Tool: Update order status.
        
        Args:
            order_id: Order identifier
            status: New status (e.g., "shipped", "delivered", "cancelled")
            
        Returns:
            JSON string with update result
        """
        success = self.order_db.update_order_status(order_id, status)
        if success:
            updated_order = self.order_db.get_order_by_id(order_id)
            return json.dumps({
                'success': True,
                'message': f'Order {order_id} status updated to {status}',
                'order': updated_order
            }, default=str)
        return json.dumps({
            'success': False,
            'error': f'Order {order_id} not found or update failed'
        })
    
    def create_support_ticket(self, order_id: str, issue: str, priority: str = 'medium') -> str:
        """
        Tool: Create a support ticket for an order.
        
        Args:
            order_id: Order identifier
            issue: Description of the issue
            priority: Ticket priority ('low', 'medium', 'high')
            
        Returns:
            JSON string with ticket information
        """
        # Verify order exists
        order = self.order_db.get_order_by_id(order_id)
        if not order:
            return json.dumps({
                'success': False,
                'error': f'Order {order_id} not found'
            })
        
        ticket = self.order_db.create_support_ticket(order_id, issue, priority)
        return json.dumps({
            'success': True,
            'ticket': ticket,
            'message': f'Support ticket {ticket["ticket_id"]} created for order {order_id}'
        }, default=str)
    
    def search_orders(self, query: str) -> str:
        """
        Tool: Search orders by customer name, email, or product.
        
        Args:
            query: Search query
            
        Returns:
            JSON string with matching orders
        """
        results = self.order_db.search_orders(query)
        return json.dumps({
            'success': True,
            'results': results,
            'count': len(results)
        }, default=str)
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Get function definitions for OpenAI/Anthropic function calling.
        
        Returns:
            List of function definitions in OpenAI format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_order_by_id",
                    "description": "Get detailed information about an order by its order ID. Use this when the customer mentions an order number or asks about a specific order.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The order ID (e.g., ORD001, 12345)"
                            }
                        },
                        "required": ["order_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_orders_by_customer",
                    "description": "Get all orders for a specific customer. Use this when you need to see a customer's order history.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "The customer ID (e.g., CUST001)"
                            }
                        },
                        "required": ["customer_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_policies",
                    "description": "Search policy documents for information about returns, warranties, shipping, refunds, etc. Use this when you need to find policy information to answer customer questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for policy information"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_order_status",
                    "description": "Update the status of an order. Use this when the customer wants to change order status or when processing an order update.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The order ID to update"
                            },
                            "status": {
                                "type": "string",
                                "description": "The new status (e.g., 'shipped', 'delivered', 'cancelled', 'processing')",
                                "enum": ["processing", "shipped", "delivered", "cancelled", "returned"]
                            }
                        },
                        "required": ["order_id", "status"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_support_ticket",
                    "description": "Create a support ticket for an order issue. Use this when a customer reports a problem that needs to be tracked.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The order ID associated with the issue"
                            },
                            "issue": {
                                "type": "string",
                                "description": "Description of the issue or problem"
                            },
                            "priority": {
                                "type": "string",
                                "description": "Priority level of the ticket",
                                "enum": ["low", "medium", "high"],
                                "default": "medium"
                            }
                        },
                        "required": ["order_id", "issue"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_orders",
                    "description": "Search for orders by customer name, email, or product name. Use this when you need to find orders but don't have the exact order ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (customer name, email, or product name)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

