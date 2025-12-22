"use client";

import React, { useState, useRef, useEffect } from "react";
import { MessageItem, Message } from "./MessageItem";
import { MessageInput } from "./MessageInput";
import { RAGThinking } from "./RAGThinking";
import { SourceCard, Source } from "./SourceCard";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";

export function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            role: "ai",
            content: "Hello! I'm your advanced AI assistant. I can help you analyze documents, answer complex queries, and visualize data. How can I assist you today?",
            timestamp: new Date().toISOString()
        }
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const [retrievedSources, setRetrievedSources] = useState<Source[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    const handleSendMessage = async (content: string, useWebSearch: boolean) => {
        // Add user message
        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content,
            timestamp: new Date().toISOString()
        };
        setMessages((prev: Message[]) => [...prev, userMsg]);
        setIsTyping(true);
        setRetrievedSources([]); // Reset sources for new query

        try {
            const response = await api.query({
                question: content,
                use_web_search: useWebSearch
            });

            // Map API retrieved chunks to SourceCard format
            const docSources: Source[] = response.retrieved_chunks.map(chunk => ({
                id: chunk.chunk_id,
                title: chunk.source,
                snippet: chunk.text,
                url: undefined
            }));

            // Map web results if available
            const webSources: Source[] = (response.web_results || []).map((res, i) => ({
                id: `web-${i}-${Date.now()}`,
                title: res.title,
                snippet: res.snippet,
                url: res.url
            }));

            setRetrievedSources([...docSources, ...webSources]);

            // Add AI response
            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "ai",
                content: response.answer,
                timestamp: new Date().toISOString()
            };
            setMessages((prev: Message[]) => [...prev, aiMsg]);
        } catch (error) {
            console.error("Query failed:", error);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "ai",
                content: "I'm sorry, I encountered an error while processing your request. Please ensure the backend is running.",
                timestamp: new Date().toISOString()
            };
            setMessages((prev: Message[]) => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
        }
    }, [messages, isTyping]);

    return (
        <div className="flex flex-col h-full w-full max-w-5xl mx-auto relative">
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-6 md:p-12 space-y-10 scroll-smooth scrollbar-hide"
            >
                <AnimatePresence initial={false}>
                    {messages.map((msg, index) => (
                        <div key={msg.id} className="relative">
                            <MessageItem message={msg} />

                            {/* Show RAG visualization after the latest AI message if sources exist */}
                            {msg.role === "ai" && index === messages.length - 1 && retrievedSources.length > 0 && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0, y: -10 }}
                                    animate={{ opacity: 1, height: "auto", y: 0 }}
                                    transition={{ type: "spring", stiffness: 200, damping: 25, delay: 0.5 }}
                                    className="pl-16 mb-10 overflow-hidden"
                                >
                                    <div className="flex gap-5 overflow-x-auto pb-6 pt-2 scrollbar-hide mask-fade-right">
                                        {retrievedSources.map((s, i) => (
                                            <SourceCard key={`${s.id}-${i}`} source={s} index={i} />
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </div>
                    ))}
                </AnimatePresence>

                {isTyping && (
                    <motion.div
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="pl-5"
                    >
                        <RAGThinking isExpanded={true} />
                    </motion.div>
                )}

                <div className="h-16" /> {/* Larger spacer for floating input bar */}
            </div>

            <div className="flex-shrink-0 z-30 absolute bottom-0 left-0 right-0 pointer-events-none">
                <div className="pointer-events-auto">
                    <MessageInput onSendMessage={handleSendMessage} isLoading={isTyping} />
                </div>
            </div>
        </div>
    );
}
