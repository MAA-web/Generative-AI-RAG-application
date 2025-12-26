const BASE_URL = 'http://localhost:5000';

export interface HealthResponse {
    status: 'healthy';
    timestamp: string;
}

export interface IngestResponse {
    success: boolean;
    document_id: string;
    chunks_created: number;
    filename: string;
}

export interface IngestBatchResponse {
    success: boolean;
    processed: number;
    failed: number;
    results: Array<{
        document_id: string;
        chunks_created: number;
        filename: string;
    }>;
    errors: Array<{
        filename: string;
        error: string;
    }>;
}

export interface ListDocumentsResponse {
    directory: string;
    total_files: number;
    files: Array<{
        filename: string;
        filepath: string;
        size: number;
        extension: string;
        modified: string;
    }>;
}

export interface QueryRequest {
    question: string;
    top_k?: number;
    use_web_search?: boolean;
    prompt_template?: 'strict' | 'balanced' | 'permissive';
}

export interface QueryResponse {
    question: string;
    answer: string;
    citations: string[];
    prompt_template?: string;
    retrieved_chunks: Array<{
        chunk_id: string;
        text: string;
        source: string;
        page: string;
        score: number;
    }>;
    web_results?: Array<{
        title: string;
        snippet: string;
        url: string;
    }>;
}

export interface WebSearchRequest {
    query: string;
    num_results?: number;
    site_filter?: string;
}

export interface WebSearchResponse {
    query: string;
    num_results: number;
    results: Array<{
        title: string;
        snippet: string;
        url: string;
        source: string;
    }>;
}

export interface StatsResponse {
    total_chunks: number;
    index_size: number;
    embedding_dimension: number;
    model: string;
}

// Customer Service Interfaces
export interface CustomerQueryRequest {
    query: string;
    customer_id?: string;
    prompt_template?: 'strict' | 'balanced' | 'permissive';
}

export interface CustomerQueryResponse {
    answer: string;
    citations: string[];
    order_found: boolean;
    order_info?: {
        order_id: string;
        customer_id: string;
        customer_name: string;
        customer_email: string;
        product_name: string;
        product_sku: string;
        quantity: number;
        price: number;
        order_date: string;
        status: string;
        shipping_address: string;
        tracking_number?: string;
        return_eligible: string;
        warranty_status: string;
        notes?: string;
    };
    customer_orders?: Array<{
        order_id: string;
        product_name: string;
        status: string;
        order_date: string;
    }>;
    retrieved_chunks: Array<{
        chunk_id: string;
        text: string;
        source: string;
        score: number;
    }>;
    prompt_template?: string;
}

export interface OrderInfo {
    order_id: string;
    customer_id: string;
    customer_name: string;
    customer_email: string;
    product_name: string;
    product_sku: string;
    quantity: number;
    price: number;
    order_date: string;
    status: string;
    shipping_address: string;
    tracking_number?: string;
    return_eligible: string;
    warranty_status: string;
    notes?: string;
}

export interface GetOrderResponse {
    success: boolean;
    order?: OrderInfo;
    formatted_context?: string;
    error?: string;
}

export interface UpdateOrderStatusRequest {
    status: string;
}

export interface UpdateOrderStatusResponse {
    success: boolean;
    message?: string;
    order?: OrderInfo;
    error?: string;
}

export interface CreateTicketRequest {
    order_id: string;
    issue: string;
    priority?: 'low' | 'medium' | 'high';
}

export interface CreateTicketResponse {
    success: boolean;
    ticket?: {
        ticket_id: string;
        order_id: string;
        issue: string;
        priority: string;
        created_at: string;
        status: string;
    };
    message?: string;
    error?: string;
}

export interface SearchOrdersRequest {
    query: string;
}

export interface SearchOrdersResponse {
    results: OrderInfo[];
    count: number;
}

export const api = {
    async getHealth(): Promise<HealthResponse> {
        const response = await fetch(`${BASE_URL}/health`);
        if (!response.ok) throw new Error('Health check failed');
        return response.json();
    },

    async ingestFile(file: File): Promise<IngestResponse> {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${BASE_URL}/ingest`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Ingestion failed');
        return response.json();
    },

    async ingestBatch(files: File[]): Promise<IngestBatchResponse> {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        const response = await fetch(`${BASE_URL}/ingest/batch`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Batch ingestion failed');
        return response.json();
    },

    async listDocuments(directory?: string): Promise<ListDocumentsResponse> {
        const url = new URL(`${BASE_URL}/ingest/list`);
        if (directory) url.searchParams.append('directory', directory);
        const response = await fetch(url.toString());
        if (!response.ok) throw new Error('Failed to list documents');
        return response.json();
    },

    async query(request: QueryRequest): Promise<QueryResponse> {
        const response = await fetch(`${BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        if (!response.ok) throw new Error('Query failed');
        return response.json();
    },

    async webSearch(request: WebSearchRequest): Promise<WebSearchResponse> {
        const response = await fetch(`${BASE_URL}/search/web`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        if (!response.ok) throw new Error('Web search failed');
        return response.json();
    },

    async getStats(): Promise<StatsResponse> {
        const response = await fetch(`${BASE_URL}/stats`);
        if (!response.ok) throw new Error('Failed to get stats');
        return response.json();
    },

    // Customer Service API Methods
    async customerQuery(request: CustomerQueryRequest): Promise<CustomerQueryResponse> {
        const response = await fetch(`${BASE_URL}/customer/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        if (!response.ok) throw new Error('Customer query failed');
        return response.json();
    },

    async getOrder(orderId: string): Promise<GetOrderResponse> {
        const response = await fetch(`${BASE_URL}/customer/order/${orderId}`);
        if (!response.ok) {
            if (response.status === 404) {
                return { success: false, error: 'Order not found' };
            }
            throw new Error('Failed to get order');
        }
        return response.json();
    },

    async updateOrderStatus(orderId: string, status: string): Promise<UpdateOrderStatusResponse> {
        const response = await fetch(`${BASE_URL}/customer/order/${orderId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status }),
        });
        if (!response.ok) {
            if (response.status === 404) {
                return { success: false, error: 'Order not found' };
            }
            throw new Error('Failed to update order status');
        }
        return response.json();
    },

    async createTicket(request: CreateTicketRequest): Promise<CreateTicketResponse> {
        const response = await fetch(`${BASE_URL}/customer/ticket`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        if (!response.ok) {
            if (response.status === 404) {
                return { success: false, error: 'Order not found' };
            }
            throw new Error('Failed to create ticket');
        }
        return response.json();
    },

    async searchOrders(request: SearchOrdersRequest): Promise<SearchOrdersResponse> {
        const response = await fetch(`${BASE_URL}/customer/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        if (!response.ok) throw new Error('Search orders failed');
        return response.json();
    }
};
