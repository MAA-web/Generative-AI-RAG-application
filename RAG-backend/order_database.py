"""
Order Database module for customer service agent.
Handles CSV-based order/transaction lookup and management.
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class OrderDatabase:
    """Manages order/transaction data from CSV file."""
    
    def __init__(self, csv_path: str = 'data/orders.csv'):
        """
        Initialize order database.
        
        Args:
            csv_path: Path to CSV file containing orders
        """
        self.csv_path = csv_path
        self.df = None
        self._load_orders()
    
    def _load_orders(self):
        """Load orders from CSV file."""
        if os.path.exists(self.csv_path):
            try:
                # Read CSV with proper handling of commas in addresses
                # Use quotechar to handle commas in quoted fields
                self.df = pd.read_csv(self.csv_path, quotechar='"', skipinitialspace=True)
                
                # Debug: Print column names to verify
                print(f"[DEBUG] CSV columns: {self.df.columns.tolist()}")
                print(f"[DEBUG] First row order_id: {self.df.iloc[0]['order_id'] if len(self.df) > 0 and 'order_id' in self.df.columns else 'N/A'}")
                
                # Strip whitespace from all string columns
                for col in self.df.columns:
                    if self.df[col].dtype == 'object':
                        self.df[col] = self.df[col].astype(str).str.strip()
                
                # Ensure order_id is string for consistent lookup
                if 'order_id' in self.df.columns:
                    self.df['order_id'] = self.df['order_id'].astype(str).str.strip().str.upper()
                    # Remove any rows where order_id is 'NAN' or empty
                    self.df = self.df[self.df['order_id'].notna()]
                    self.df = self.df[self.df['order_id'] != '']
                    self.df = self.df[self.df['order_id'] != 'NAN']
                else:
                    print(f"[ERROR] 'order_id' column not found in CSV! Available columns: {self.df.columns.tolist()}")
                    self._create_empty_db()
                    return
                
                # Remove any empty rows
                self.df = self.df.dropna(subset=['order_id'])
                self.df = self.df[self.df['order_id'] != '']
                
                print(f"Loaded {len(self.df)} orders from {self.csv_path}")
                if len(self.df) > 0:
                    print(f"Sample order IDs: {self.df['order_id'].head().tolist()}")
            except Exception as e:
                print(f"Error loading orders: {e}")
                import traceback
                traceback.print_exc()
                self._create_empty_db()
        else:
            self._create_empty_db()
            print(f"Warning: {self.csv_path} not found. Creating empty database.")
    
    def _create_empty_db(self):
        """Create empty dataframe with expected columns."""
        self.df = pd.DataFrame(columns=[
            'order_id', 'customer_id', 'customer_name', 'customer_email',
            'product_name', 'product_sku', 'quantity', 'price', 
            'order_date', 'status', 'shipping_address', 'tracking_number',
            'return_eligible', 'warranty_status', 'notes'
        ])
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve order by order ID.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order dictionary or None if not found
        """
        if self.df is None or self.df.empty:
            print(f"[DEBUG] Database is empty or None")
            return None
        
        # Normalize order ID: strip, uppercase, remove any extra whitespace
        order_id = str(order_id).strip().upper()
        print(f"[DEBUG] Looking up order ID (normalized): '{order_id}'")
        print(f"[DEBUG] Database has {len(self.df)} orders")
        print(f"[DEBUG] Available order IDs: {self.df['order_id'].tolist()}")
        
        # Try exact match
        order = self.df[self.df['order_id'] == order_id]
        
        if order.empty:
            # Try case-insensitive match as fallback
            order = self.df[self.df['order_id'].str.upper() == order_id]
            if order.empty:
                print(f"[DEBUG] Order ID '{order_id}' not found (tried exact and case-insensitive match)")
                return None
        
        # Convert to dictionary, handling NaN values
        order_dict = order.iloc[0].to_dict()
        # Convert NaN to None for JSON serialization
        for key, value in order_dict.items():
            if pd.isna(value):
                order_dict[key] = None
            elif isinstance(value, (pd.Timestamp, datetime)):
                order_dict[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
        
        return order_dict
    
    def get_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all orders for a customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of order dictionaries
        """
        if self.df is None or self.df.empty:
            return []
        
        customer_id = str(customer_id).strip()
        orders = self.df[self.df['customer_id'] == customer_id]
        
        # Convert to list of dictionaries
        orders_list = orders.to_dict('records')
        # Clean NaN values
        for order in orders_list:
            for key, value in list(order.items()):
                if pd.isna(value):
                    order[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    order[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
        
        return orders_list
    
    def search_orders(self, query: str) -> List[Dict[str, Any]]:
        """
        Search orders by customer name, email, or product name.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching order dictionaries
        """
        if self.df is None or self.df.empty:
            return []
        
        query = query.lower().strip()
        # Search across multiple columns
        mask = (
            self.df['customer_name'].astype(str).str.lower().str.contains(query, na=False) |
            self.df['customer_email'].astype(str).str.lower().str.contains(query, na=False) |
            self.df['product_name'].astype(str).str.lower().str.contains(query, na=False) |
            self.df['order_id'].astype(str).str.contains(query, na=False)
        )
        
        orders = self.df[mask]
        orders_list = orders.to_dict('records')
        
        # Clean NaN values
        for order in orders_list:
            for key, value in list(order.items()):
                if pd.isna(value):
                    order[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    order[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
        
        return orders_list
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """
        Update order status.
        
        Args:
            order_id: Order identifier
            status: New status
            
        Returns:
            True if updated, False if order not found
        """
        if self.df is None or self.df.empty:
            return False
        
        order_id = str(order_id).strip()
        if order_id not in self.df['order_id'].values:
            return False
        
        self.df.loc[self.df['order_id'] == order_id, 'status'] = status
        self._save_orders()
        return True
    
    def create_support_ticket(self, order_id: str, issue: str, priority: str = 'medium') -> Dict[str, Any]:
        """
        Create a support ticket for an order.
        
        Args:
            order_id: Order identifier
            issue: Description of the issue
            priority: Ticket priority ('low', 'medium', 'high')
            
        Returns:
            Ticket information
        """
        ticket = {
            'ticket_id': f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'order_id': order_id,
            'issue': issue,
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }
        
        # Save to tickets CSV if it exists, otherwise just return
        tickets_path = 'data/support_tickets.csv'
        try:
            if os.path.exists(tickets_path):
                tickets_df = pd.read_csv(tickets_path)
            else:
                tickets_df = pd.DataFrame(columns=['ticket_id', 'order_id', 'issue', 'priority', 'created_at', 'status'])
            
            tickets_df = pd.concat([tickets_df, pd.DataFrame([ticket])], ignore_index=True)
            os.makedirs(os.path.dirname(tickets_path), exist_ok=True)
            tickets_df.to_csv(tickets_path, index=False)
        except Exception as e:
            print(f"Warning: Could not save ticket to CSV: {e}")
        
        return ticket
    
    def _save_orders(self):
        """Save orders back to CSV."""
        if self.df is not None:
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            self.df.to_csv(self.csv_path, index=False)
    
    def format_order_context(self, order: Dict[str, Any]) -> str:
        """
        Format order information as context string for LLM.
        
        Args:
            order: Order dictionary
            
        Returns:
            Formatted context string
        """
        context = f"""Order Information:
- Order ID: {order.get('order_id', 'N/A')}
- Customer: {order.get('customer_name', 'N/A')} (ID: {order.get('customer_id', 'N/A')})
- Email: {order.get('customer_email', 'N/A')}
- Product: {order.get('product_name', 'N/A')} (SKU: {order.get('product_sku', 'N/A')})
- Quantity: {order.get('quantity', 'N/A')}
- Price: ${order.get('price', 'N/A')}
- Order Date: {order.get('order_date', 'N/A')}
- Status: {order.get('status', 'N/A')}
- Shipping Address: {order.get('shipping_address', 'N/A')}
- Tracking Number: {order.get('tracking_number', 'N/A')}
- Return Eligible: {order.get('return_eligible', 'N/A')}
- Warranty Status: {order.get('warranty_status', 'N/A')}
"""
        if order.get('notes'):
            context += f"- Notes: {order.get('notes')}\n"
        
        return context

