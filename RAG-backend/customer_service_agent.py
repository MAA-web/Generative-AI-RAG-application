"""
Customer Service Agent with function calling capabilities.
Combines order lookup, policy retrieval, and action execution.
"""

import re
from typing import Dict, List, Any, Optional
from order_database import OrderDatabase
from rag_pipeline import RAGPipeline

class CustomerServiceAgent:
    """Customer service agent with order lookup and policy retrieval."""
    
    def __init__(self, order_db: OrderDatabase, rag_pipeline: RAGPipeline):
        """
        Initialize customer service agent.
        
        Args:
            order_db: Order database instance
            rag_pipeline: RAG pipeline for policy retrieval
        """
        self.order_db = order_db
        self.rag_pipeline = rag_pipeline
    
    def extract_order_id(self, query: str) -> Optional[str]:
        """
        Extract order ID from user query.
        
        Args:
            query: User query text
            
        Returns:
            Order ID if found, None otherwise
        """
        # First, try to find order ID pattern (ORD### format) anywhere in the query
        # This is the most reliable pattern
        order_id_pattern = r'\b([A-Z]{3,4}\d{3,6})\b'
        match = re.search(order_id_pattern, query, re.IGNORECASE)
        if match:
            order_id = match.group(1).strip().upper()
            print(f"[DEBUG] Extracted order ID (pattern match): {order_id} from query: {query}")
            return order_id
        
        # Common patterns: "order 12345", "order #12345", "order ID: 12345", "my order id is ORD004", etc.
        # Order matters - more specific patterns first
        patterns = [
            r'order\s+id\s+is\s+([A-Z0-9]{3,20})',  # "order id is ORD004" - most specific
            r'order\s+id[:\s]+([A-Z0-9]{3,20})',  # "order id: ORD004" or "order id ORD004"
            r'order\s*#?\s*([A-Z0-9]{3,20})',  # "order ORD004" or "order #ORD004"
            r'order\s+([A-Z0-9]{3,20})',  # "order ORD004"
            r'#([A-Z0-9]{3,20})',  # Just a hash followed by alphanumeric "#ORD004"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                order_id = match.group(1).strip().upper()
                # Validate it looks like an order ID (not just "ID" or "is")
                if len(order_id) >= 3 and order_id not in ['ID', 'IS', 'THE', 'MY', 'IS']:
                    print(f"[DEBUG] Extracted order ID (regex): {order_id} from query: {query}")
                    return order_id
        
        # Check if query itself is just an order ID (alphanumeric, 5-20 chars)
        if re.match(r'^[A-Z0-9]{5,20}$', query.strip(), re.IGNORECASE):
            order_id = query.strip().upper()
            print(f"[DEBUG] Query is order ID: {order_id}")
            return order_id
        
        print(f"[DEBUG] No order ID found in query: {query}")
        return None
    
    def process_customer_query(self, query: str, customer_id: Optional[str] = None, prompt_template: str = 'balanced') -> Dict[str, Any]:
        """
        Process customer service query with order lookup and policy retrieval.
        
        Args:
            query: Customer query/question
            customer_id: Optional customer ID for context
            
        Returns:
            Dictionary with answer, order info, and policy context
        """
        # Step 1: Try to extract order ID from query
        order_id = self.extract_order_id(query)
        order_info = None
        order_context = ""
        
        # Step 2: Look up order if ID found
        if order_id:
            print(f"[DEBUG] Looking up order ID: {order_id}")
            order_info = self.order_db.get_order_by_id(order_id)
            if order_info:
                print(f"[DEBUG] Order found: {order_info.get('order_id')} - {order_info.get('product_name')} - Status: {order_info.get('status')}")
                order_context = self.order_db.format_order_context(order_info)
            else:
                print(f"[DEBUG] Order ID {order_id} NOT FOUND in database")
                # Try to check what order IDs are available (for debugging)
                if hasattr(self.order_db, 'df') and self.order_db.df is not None and not self.order_db.df.empty:
                    available_ids = self.order_db.df['order_id'].astype(str).tolist()
                    print(f"[DEBUG] Available order IDs in database: {available_ids}")
                order_context = f"Note: Order ID {order_id} was mentioned but not found in the system."
        
        # Step 3: Also try customer ID lookup if provided
        customer_orders = []
        if customer_id:
            customer_orders = self.order_db.get_orders_by_customer(customer_id)
        
        # Step 4: Retrieve relevant policy documents
        policy_chunks = self.rag_pipeline.retrieve(query, top_k=5)
        
        # Step 5: Build enhanced context by adding order info to chunks metadata
        # We'll create a special "order context chunk" to include in the context
        enhanced_chunks = list(policy_chunks) if policy_chunks else []
        
        # Add order context as a special chunk if order found
        if order_context:
            order_chunk = {
                'text': order_context,
                'metadata': {'source': 'order_database', 'type': 'order_info'},
                'chunk_id': f'order_{order_id}' if order_id else 'order_info'
            }
            enhanced_chunks.insert(0, order_chunk)  # Add at beginning for priority
        
        # Add customer order history if available
        if customer_orders and len(customer_orders) > 0:
            history_text = f"Customer Order History ({len(customer_orders)} orders):\n"
            for i, order in enumerate(customer_orders[:5], 1):
                history_text += f"{i}. Order {order.get('order_id')} - {order.get('product_name')} - Status: {order.get('status')}\n"
            
            history_chunk = {
                'text': history_text,
                'metadata': {'source': 'order_database', 'type': 'customer_history'},
                'chunk_id': f'customer_history_{customer_id}' if customer_id else 'customer_history'
            }
            enhanced_chunks.insert(1, history_chunk)  # Add after order info
        
        # Step 6: Generate answer with enhanced context
        answer, citations = self.rag_pipeline.generate_answer(
            question=query,
            context_chunks=enhanced_chunks,
            use_web_search=False,
            web_results=None,
            prompt_template=prompt_template
        )
        
        # Step 7: Build response
        response = {
            'answer': answer,
            'citations': citations,
            'order_found': order_info is not None,
            'order_info': order_info,
            'retrieved_chunks': [
                {
                    'chunk_id': chunk['chunk_id'],
                    'text': chunk['text'][:200] + '...',
                    'source': chunk['metadata']['source'],
                    'score': chunk.get('score', 0.0)
                }
                for chunk in policy_chunks
            ]
        }
        
        if customer_orders:
            response['customer_orders'] = customer_orders[:5]  # Limit response size
        
        return response
    
    def get_order_info(self, order_id: str) -> Dict[str, Any]:
        """
        Get order information by ID.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order information dictionary
        """
        order = self.order_db.get_order_by_id(order_id)
        if order:
            return {
                'success': True,
                'order': order,
                'formatted_context': self.order_db.format_order_context(order)
            }
        return {
            'success': False,
            'error': f'Order {order_id} not found'
        }
    
    def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """
        Update order status.
        
        Args:
            order_id: Order identifier
            status: New status
            
        Returns:
            Update result dictionary
        """
        success = self.order_db.update_order_status(order_id, status)
        if success:
            updated_order = self.order_db.get_order_by_id(order_id)
            return {
                'success': True,
                'message': f'Order {order_id} status updated to {status}',
                'order': updated_order
            }
        return {
            'success': False,
            'error': f'Order {order_id} not found or update failed'
        }
    
    def create_support_ticket(self, order_id: str, issue: str, priority: str = 'medium') -> Dict[str, Any]:
        """
        Create a support ticket.
        
        Args:
            order_id: Order identifier
            issue: Issue description
            priority: Ticket priority
            
        Returns:
            Ticket information
        """
        # Verify order exists
        order = self.order_db.get_order_by_id(order_id)
        if not order:
            return {
                'success': False,
                'error': f'Order {order_id} not found'
            }
        
        ticket = self.order_db.create_support_ticket(order_id, issue, priority)
        return {
            'success': True,
            'ticket': ticket,
            'message': f'Support ticket {ticket["ticket_id"]} created for order {order_id}'
        }

