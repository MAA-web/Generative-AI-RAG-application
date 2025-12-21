"use client";

import React, { useState, useRef, useEffect } from "react";
import { MessageItem, Message } from "./MessageItem";
import { MessageInput } from "./MessageInput";
import { RAGThinking } from "./RAGThinking";
import { SourceCard, Source } from "./SourceCard";
import { motion, AnimatePresence } from "framer-motion";

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
    const scrollRef = useRef<HTMLDivElement>(null);

    // Mock sources for demonstration
    const mockSources: Source[] = [
        {
            id: "s1",
            title: "Introduction to Neural Networks.pdf",
            snippet: "Neural networks are computing systems inspired by the biological neural networks that constitute animal brains...",
            url: "#"
        },
        {
            id: "s2",
            title: "Transformer Architecture Research",
            snippet: "The Transformer is a deep learning model that adopts the mechanism of self-attention, differentially weighing the significance...",
            url: "#"
        },
        {
            id: "s3",
            title: "RAG Overview 2024",
            snippet: "Retrieval-Augmented Generation (RAG) is a technique that enhances the accuracy and reliability of generative AI models...",
        }
    ];

    const handleSendMessage = async (content: string) => {
        // Add user message
        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        // Simulate AI response delay and "thinking"
        setTimeout(() => {
            // Add AI response
            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "ai",
                content: "The RAG (Retrieval-Augmented Generation) architecture fundamentally merges neural generation with precise information retrieval [1]. By grounding the model in external curated knowledge [2], it dramatically reduces hallucinations and ensures that responses are always contextually relevant and factual [3].",
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, aiMsg]);
            setIsTyping(false);
        }, 3000);
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

                            {/* Show RAG visualization after specific AI messages (mock logic) */}
                            {msg.role === "ai" && index === messages.length - 1 && index > 0 && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0, y: -10 }}
                                    animate={{ opacity: 1, height: "auto", y: 0 }}
                                    transition={{ type: "spring", stiffness: 200, damping: 25, delay: 0.8 }}
                                    className="pl-16 mb-10 overflow-hidden"
                                >
                                    <div className="flex gap-5 overflow-x-auto pb-6 pt-2 scrollbar-hide mask-fade-right">
                                        {mockSources.map((s, i) => (
                                            <SourceCard key={s.id} source={s} index={i} />
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
