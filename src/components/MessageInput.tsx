"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Mic, Image as ImageIcon, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import clsx from "clsx";

interface MessageInputProps {
    onSendMessage: (content: string) => void;
    isLoading?: boolean;
}

export function MessageInput({ onSendMessage, isLoading }: MessageInputProps) {
    const [content, setContent] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = () => {
        if (!content.trim() || isLoading) return;
        onSendMessage(content);
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
                    <textarea
                        ref={textareaRef}
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask AI anything..."
                        className="w-full bg-transparent border-none focus:ring-0 resize-none max-h-48 min-h-[60px] py-4 px-6 text-[16px] md:text-[18px] font-medium placeholder:text-muted-foreground/30 scrollbar-hide leading-snug"
                        rows={1}
                    />

                    <div className="flex items-center justify-between px-3 pb-2 pt-1">
                        <div className="flex items-center gap-2">
                            <button className="p-3 rounded-[1.25rem] text-muted-foreground hover:bg-white/5 hover:text-foreground transition-all active:scale-90">
                                <Paperclip size={20} />
                            </button>
                            <button className="p-3 rounded-[1.25rem] text-muted-foreground hover:bg-white/5 hover:text-foreground transition-all active:scale-90">
                                <ImageIcon size={20} />
                            </button>
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
