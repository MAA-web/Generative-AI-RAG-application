"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Loader2, Sparkles, Brain } from "lucide-react";
import clsx from "clsx";

interface RAGThinkingProps {
    steps?: string[];
    isExpanded?: boolean;
}

export function RAGThinking({
    steps = ["Analyzing query...", "Retrieving relevant documents...", "Synthesizing answer..."],
    isExpanded: defaultExpanded = true
}: RAGThinkingProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className="w-full max-w-2xl mb-6">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors mb-3 pl-2"
            >
                <div className="relative">
                    <Brain size={16} className="text-primary" />
                    <motion.div
                        className="absolute -top-1 -right-1"
                        animate={{ opacity: [0, 1, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <Sparkles size={8} className="text-yellow-400" />
                    </motion.div>
                </div>
                <span>Thinking Process</span>
                <ChevronDown
                    size={14}
                    className={clsx("transition-transform duration-200", isExpanded ? "rotate-180" : "")}
                />
            </button>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        className="overflow-hidden"
                    >
                        <div className="pl-4 border-l-2 border-border/50 space-y-3 pb-2">
                            {steps.map((step, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ x: -10, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className="flex items-center gap-3 text-sm text-muted-foreground/80"
                                >
                                    {idx === steps.length - 1 ? (
                                        <Loader2 size={14} className="animate-spin text-primary" />
                                    ) : (
                                        <div className="w-3.5 h-3.5 rounded-full bg-primary/20 flex items-center justify-center">
                                            <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                                        </div>
                                    )}
                                    <span>{step}</span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
