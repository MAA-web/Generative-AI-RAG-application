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
    steps = ["Indexing knowledge base...", "Retrieving relevant context...", "Synthesizing response..."],
    isExpanded: defaultExpanded = true
}: RAGThinkingProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className="w-full max-w-2xl mb-8 ml-2">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-3 text-sm font-bold text-muted-foreground/80 hover:text-foreground transition-all mb-4 pl-3"
            >
                <div className="relative">
                    <div className="w-7 h-7 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Brain size={16} className="text-primary" />
                    </div>
                    <motion.div
                        className="absolute -top-1 -right-1"
                        animate={{ opacity: [0, 1, 0], scale: [0.8, 1.2, 0.8] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <Sparkles size={10} className="text-yellow-400" />
                    </motion.div>
                </div>
                <span className="tracking-tight">Processing Pipeline</span>
                <ChevronDown
                    size={14}
                    className={clsx("transition-transform duration-300", isExpanded ? "rotate-180" : "")}
                />
            </button>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0, y: -10 }}
                        animate={{ height: "auto", opacity: 1, y: 0 }}
                        exit={{ height: 0, opacity: 0, y: -10 }}
                        transition={{ type: "spring", stiffness: 200, damping: 20 }}
                        className="overflow-hidden"
                    >
                        <div className="pl-6 border-l-2 border-white/5 space-y-4 pb-4">
                            {steps.map((step, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ x: -10, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: idx * 0.15 }}
                                    className="flex items-center gap-4 text-[13px] font-medium text-muted-foreground"
                                >
                                    {idx === steps.length - 1 ? (
                                        <Loader2 size={14} className="animate-spin text-primary" />
                                    ) : (
                                        <div className="w-5 h-5 rounded-lg bg-white/5 flex items-center justify-center border border-white/5 shadow-inner">
                                            <div className="w-1.5 h-1.5 rounded-full bg-primary/60 shadow-[0_0_8px_rgba(0,113,227,0.5)]" />
                                        </div>
                                    )}
                                    <span className="opacity-80 tracking-tight">{step}</span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
