const BASE_URL = 'http://10.1.56.215:5000';

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
}

export interface QueryResponse {
    question: string;
    answer: string;
    citations: string[];
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
    }
};
