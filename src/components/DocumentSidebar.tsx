"use client";

import React, { useState, useEffect } from "react";
import {
    FileText,
    Upload,
    Database,
    Info,
    CheckCircle2,
    AlertCircle,
    Loader2,
    Layers,
    Files
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api, ListDocumentsResponse, StatsResponse } from "@/lib/api";

export function DocumentSidebar() {
    const [docs, setDocs] = useState<ListDocumentsResponse | null>(null);
    const [stats, setStats] = useState<StatsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadTime, setUploadTime] = useState(0);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let timer: any;
        if (uploading) {
            timer = setInterval(() => {
                setUploadTime(prev => prev + 1);
            }, 1000);
        } else {
            setUploadTime(0);
        }
        return () => clearInterval(timer);
    }, [uploading]);

    const fetchData = async () => {
        try {
            const [docsData, statsData] = await Promise.all([
                api.listDocuments(),
                api.getStats()
            ]);
            setDocs(docsData);
            setStats(statsData);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch sidebar data:", err);
            setError("Cannot connect to backend");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        // Check for large files (> 10MB) to warn user
        const largeFiles = Array.from(files).filter(f => f.size > 10 * 1024 * 1024);
        if (largeFiles.length > 0) {
            const proceed = confirm(`Large file(s) detected: ${largeFiles.map(f => f.name).join(', ')}. Ingestion may take several minutes. Continue?`);
            if (!proceed) return;
        }

        setUploading(true);
        setError(null);
        try {
            // Set a long timeout for ingestion (5 minutes)
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300000);

            if (files.length === 1) {
                await api.ingestFile(files[0]);
            } else {
                await api.ingestBatch(Array.from(files));
            }
            clearTimeout(timeoutId);
            await fetchData();
        } catch (err: any) {
            console.error("Upload failed:", err);
            if (err.name === 'AbortError') {
                setError("Ingestion timed out. The file might still be processing on the server.");
            } else {
                setError("Upload failed. Check backend connectivity.");
            }
        } finally {
            setUploading(false);
            event.target.value = ''; // Reset input
        }
    };

    return (
        <div className="w-80 h-full flex flex-col border-r border-white/10 liquid-glass p-6 gap-8 overflow-y-auto">
            <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-primary/20 text-primary">
                    <Database size={24} />
                </div>
                <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                    Knowledge Base
                </h2>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-2 gap-3">
                <div className="p-4 rounded-[1.5rem] bg-white/5 border border-white/5">
                    <div className="text-muted-foreground mb-1 flex items-center gap-1.5">
                        <Layers size={14} />
                        <span className="text-xs uppercase tracking-wider font-semibold">Chunks</span>
                    </div>
                    <div className="text-xl font-bold">
                        {loading ? <Loader2 size={16} className="animate-spin" /> : stats?.total_chunks || 0}
                    </div>
                </div>
                <div className="p-4 rounded-[1.5rem] bg-white/5 border border-white/5">
                    <div className="text-muted-foreground mb-1 flex items-center gap-1.5">
                        <Files size={14} />
                        <span className="text-xs uppercase tracking-wider font-semibold">Docs</span>
                    </div>
                    <div className="text-xl font-bold">
                        {loading ? <Loader2 size={16} className="animate-spin" /> : docs?.total_files || 0}
                    </div>
                </div>
            </div>

            {/* Upload Area */}
            <div className="space-y-3">
                <label className="text-xs uppercase tracking-widest font-bold text-muted-foreground ml-1">
                    Ingest Content
                </label>
                <div className="relative">
                    <input
                        type="file"
                        multiple
                        accept=".pdf,.txt,.md"
                        className="hidden"
                        id="file-upload"
                        onChange={handleFileUpload}
                        disabled={uploading}
                    />
                    <label
                        htmlFor="file-upload"
                        className="flex flex-col items-center justify-center p-8 rounded-[2rem] border-2 border-dashed border-white/10 hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer group"
                    >
                        {uploading ? (
                            <div className="flex flex-col items-center">
                                <Loader2 className="animate-spin text-primary mb-2" size={32} />
                                <span className="text-xs font-mono text-primary animate-pulse">
                                    {Math.floor(uploadTime / 60)}:{(uploadTime % 60).toString().padStart(2, '0')}
                                </span>
                            </div>
                        ) : (
                            <Upload className="text-muted-foreground group-hover:text-primary transition-colors mb-2" size={32} />
                        )}
                        <span className="text-sm font-medium text-foreground">
                            {uploading ? "Extracting & Embedding..." : "Drop files here"}
                        </span>
                        <span className="text-xs text-muted-foreground mt-1 text-center">
                            {uploading ? "Processing knowledge chunks" : "PDF, TXT, or MD"}
                        </span>
                    </label>
                </div>
            </div>

            {/* Document List */}
            <div className="flex-1 flex flex-col gap-4 min-h-0">
                <label className="text-xs uppercase tracking-widest font-bold text-muted-foreground ml-1">
                    Available Sources
                </label>

                <div className="flex-1 overflow-y-auto space-y-2 pr-2 scrollbar-hide">
                    <AnimatePresence>
                        {docs?.files.map((file, idx) => (
                            <motion.div
                                key={file.filename}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="group flex items-center gap-3 p-3 rounded-2xl hover:bg-white/5 border border-transparent hover:border-white/5 transition-all cursor-default"
                            >
                                <div className="p-2 rounded-xl bg-white/5 text-muted-foreground group-hover:text-foreground transition-colors">
                                    <FileText size={18} />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="text-sm font-medium truncate">{file.filename}</div>
                                    <div className="text-[10px] text-muted-foreground uppercase tracking-tight">
                                        {(file.size / 1024).toFixed(1)} KB • {file.extension}
                                    </div>
                                </div>
                                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                    <CheckCircle2 size={16} className="text-green-500" />
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {!loading && docs?.files.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-12 text-muted-foreground bg-white/5 rounded-3xl border border-dashed border-white/10">
                            <Info size={24} className="mb-2 opacity-20" />
                            <p className="text-xs font-medium">No documents yet</p>
                        </div>
                    )}

                    {error && (
                        <div className="flex items-center gap-2 p-3 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs">
                            <AlertCircle size={14} />
                            <span>{error}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* System Info */}
            {stats && (
                <div className="pt-4 border-t border-white/5">
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground uppercase tracking-widest font-bold px-1">
                        <span>Model</span>
                        <span className="text-primary truncate ml-4 max-w-[120px]">{stats.model.split('/').pop()}</span>
                    </div>
                </div>
            )}
        </div>
    );
}
