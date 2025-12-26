# Customer Service Agent System

This document describes the customer service agent functionality that combines order lookup, policy retrieval, and intelligent query processing.

## Overview

The customer service agent extends the RAG system to provide comprehensive customer support by:
- Automatically extracting order IDs from customer queries
- Looking up order information from CSV database
- Retrieving relevant policy documents
- Generating contextual answers with order and policy information
- Supporting order status updates and ticket creation

## Features

### 1. Automatic Order ID Extraction
The system automatically detects order IDs in natural language queries:
- "What's the status of order #12345?"
- "I want to return order 12345"
- "Order ID: 12345"

### 2. Rich Context Combination
Combines multiple sources of information:
- **Order Information**: Customer details, product info, status, tracking
- **Policy Documents**: Relevant return/warranty/shipping policies
- **Customer History**: Previous orders for the customer

### 3. Action Capabilities
- Update order status
- Create support tickets
- Search orders by customer/email/product

## API Endpoints

### POST `/customer/query`
Main customer service query endpoint.

**Request:**
```json
{
    "query": "What's the status of order #ORD001?",
    "customer_id": "CUST001",
    "prompt_template": "balanced"
}
```

**Response:**
```json
{
    "answer": "Based on your order information...",
    "order_found": true,
    "order_info": {
        "order_id": "ORD001",
        "customer_name": "John Smith",
        "product_name": "Wireless Mouse",
        "status": "delivered",
        ...
    },
    "citations": [...],
    "retrieved_chunks": [...]
}
```

### GET `/customer/order/<order_id>`
Get detailed order information.

**Response:**
```json
{
    "success": true,
    "order": {...},
    "formatted_context": "Order Information:\n..."
}
```

### PUT `/customer/order/<order_id>/status`
Update order status.

**Request:**
```json
{
    "status": "shipped"
}
```

### POST `/customer/ticket`
Create a support ticket.

**Request:**
```json
{
    "order_id": "ORD001",
    "issue": "Product arrived damaged",
    "priority": "high"
}
```

### POST `/customer/search`
Search orders by customer name, email, or product.

**Request:**
```json
{
    "query": "john@example.com"
}
```

## CSV Database Structure

The orders CSV file (`data/orders.csv`) should have the following columns:

- `order_id`: Unique order identifier
- `customer_id`: Customer identifier
- `customer_name`: Customer full name
- `customer_email`: Customer email address
- `product_name`: Product name
- `product_sku`: Product SKU
- `quantity`: Quantity ordered
- `price`: Order price
- `order_date`: Order date
- `status`: Order status (processing, shipped, delivered, etc.)
- `shipping_address`: Shipping address
- `tracking_number`: Tracking number (optional)
- `return_eligible`: Return eligibility (Yes/No)
- `warranty_status`: Warranty status
- `notes`: Additional notes

## Example Usage

### Frontend TypeScript
```typescript
import { api } from '@/lib/api';

// Customer query with order lookup
const response = await api.customerQuery({
    query: "I want to return order #ORD001",
    customer_id: "CUST001"
});

console.log(response.answer);
console.log(response.order_info);

// Get order details
const order = await api.getOrder("ORD001");

// Update order status
await api.updateOrderStatus("ORD001", "shipped");

// Create support ticket
const ticket = await api.createTicket({
    order_id: "ORD001",
    issue: "Product defective",
    priority: "high"
});
```

### Python/Backend
```python
from customer_service_agent import CustomerServiceAgent
from order_database import OrderDatabase
from rag_pipeline import RAGPipeline

# Initialize components
order_db = OrderDatabase('data/orders.csv')
agent = CustomerServiceAgent(order_db, rag_pipeline)

# Process customer query
result = agent.process_customer_query(
    query="What's the status of order #ORD001?",
    customer_id="CUST001"
)

print(result['answer'])
print(result['order_info'])
```

## Configuration

Set the orders CSV path via environment variable:
```bash
export ORDERS_CSV_PATH='data/orders.csv'
```

Or it defaults to `data/orders.csv` in the RAG-backend directory.

## Integration with Existing RAG System

The customer service agent leverages the existing RAG pipeline:
- Uses the same policy document retrieval
- Supports all three prompt templates (strict, balanced, permissive)
- Maintains citation and source tracking
- Integrates with web search (if enabled)

## Workflow

1. **Query Processing**: Customer submits query
2. **Order ID Extraction**: System extracts order ID from query
3. **Order Lookup**: Retrieves order information from CSV
4. **Policy Retrieval**: Searches policy documents for relevant information
5. **Context Building**: Combines order info + policies + customer history
6. **Answer Generation**: LLM generates comprehensive answer
7. **Response**: Returns answer with order info, citations, and retrieved chunks

## Future Enhancements

- Database integration (PostgreSQL, SQLite) instead of CSV
- Real-time order status updates
- Email notifications
- Chat history tracking
- Multi-language support
- Advanced analytics and reporting

