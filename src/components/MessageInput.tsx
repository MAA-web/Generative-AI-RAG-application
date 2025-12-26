"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Mic, Image as ImageIcon, Loader2, Globe } from "lucide-react";
import { motion } from "framer-motion";
import clsx from "clsx";

interface MessageInputProps {
    onSendMessage: (content: string, useWebSearch: boolean, promptTemplate: 'strict' | 'balanced' | 'permissive', mode: 'general' | 'customer') => void;
    isLoading?: boolean;
    currentMode: 'general' | 'customer';
    onModeChange: (mode: 'general' | 'customer') => void;
}

export function MessageInput({ onSendMessage, isLoading, currentMode, onModeChange }: MessageInputProps) {
    const [content, setContent] = useState("");
    const [useWebSearch, setUseWebSearch] = useState(false);
    const [promptTemplate, setPromptTemplate] = useState<'strict' | 'balanced' | 'permissive'>('balanced');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = () => {
        if (!content.trim() || isLoading) return;
        onSendMessage(content, useWebSearch, promptTemplate, currentMode);
        setContent("");
    };

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
        }
    }, [content]);

    return (
        <div className="w-full max-w-4xl mx-auto px-6 pb-10 mt-2">
            <motion.div
                layout
                className="relative group group-focus-within:scale-[1.01] transition-transform duration-500 will-change-transform"
            >
                <div className="absolute inset-0 bg-primary/20 blur-3xl opacity-0 group-focus-within:opacity-40 transition-opacity duration-700" />

                <div className="relative liquid-glass border border-white/20 rounded-[2.5rem] p-3 shadow-2xl transition-all">
                    <div className="flex gap-2 mb-2 p-2 px-3 border-b border-white/5">
                        {(['general', 'customer'] as const).map((m) => (
                            <button
                                key={m}
                                onClick={() => onModeChange(m)}
                                className={clsx(
                                    "px-4 py-2 rounded-2xl text-[11px] font-bold uppercase tracking-wider transition-all flex items-center gap-2",
                                    currentMode === m
                                        ? "bg-white/10 text-white shadow-lg"
                                        : "text-white/30 hover:text-white/60 hover:bg-white/5"
                                )}
                            >
                                <span className={clsx("w-2 h-2 rounded-full", currentMode === m ? "bg-primary animate-pulse" : "bg-white/20")} />
                                {m === 'general' ? 'Advanced AI' : 'Customer Support'}
                            </button>
                        ))}
                    </div>

                    <textarea
                        ref={textareaRef}
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={currentMode === 'customer' ? "Enter your order ID or question..." : "Ask AI anything..."}
                        className="w-full bg-transparent border-none focus:ring-0 resize-none max-h-48 min-h-[60px] py-4 px-6 text-[16px] md:text-[18px] font-medium placeholder:text-muted-foreground/30 scrollbar-hide leading-snug"
                        rows={1}
                    />

                    <div className="flex items-center justify-between px-3 pb-2 pt-1">
                        <div className="flex items-center gap-2">
                            <button className="p-3 rounded-[1.25rem] text-muted-foreground hover:bg-white/5 hover:text-foreground transition-all active:scale-90">
                                <Paperclip size={20} />
                            </button>
                            <button
                                onClick={() => setUseWebSearch(!useWebSearch)}
                                className={clsx(
                                    "p-3 rounded-[1.25rem] transition-all active:scale-90 flex items-center gap-2",
                                    useWebSearch ? "text-primary bg-primary/10" : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                                )}
                            >
                                <Globe size={20} />
                                {useWebSearch && <span className="text-xs font-bold uppercase tracking-wider">Web Search</span>}
                            </button>
                            <div className="h-6 w-px bg-white/10 mx-1" />
                            <div className="flex bg-white/5 rounded-2xl p-1 gap-1">
                                {(['strict', 'balanced', 'permissive'] as const).map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setPromptTemplate(t)}
                                        className={clsx(
                                            "px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all",
                                            promptTemplate === t
                                                ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                                : "text-muted-foreground/50 hover:text-foreground hover:bg-white/5"
                                        )}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <button className="p-3 rounded-[1.25rem] text-muted-foreground hover:bg-white/5 hover:text-foreground transition-all active:scale-90">
                                <Mic size={20} />
                            </button>
                            <button
                                onClick={handleSend}
                                disabled={!content.trim() || isLoading}
                                className={clsx(
                                    "p-3.5 rounded-2xl transition-all duration-300 shadow-xl",
                                    content.trim() && !isLoading
                                        ? "bg-primary text-primary-foreground shadow-primary/30 hover:scale-110 active:scale-95 translate-y-[-2px]"
                                        : "bg-white/5 text-muted-foreground/30 cursor-not-allowed"
                                )}
                            >
                                {isLoading ? (
                                    <Loader2 size={20} className="animate-spin" />
                                ) : (
                                    <Send size={20} strokeWidth={2.5} />
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
