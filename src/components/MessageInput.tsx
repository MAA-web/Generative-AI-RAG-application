"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Mic, Image as ImageIcon } from "lucide-react";
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
        <div className="w-full max-w-4xl mx-auto px-4 pb-6">
            <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-blue-500/10 to-purple-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="relative bg-secondary/80 backdrop-blur-xl border border-border/50 rounded-2xl p-2 shadow-lg transition-colors focus-within:bg-secondary focus-within:border-primary/30">
                    <textarea
                        ref={textareaRef}
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask anything..."
                        className="w-full bg-transparent border-none focus:ring-0 resize-none max-h-40 min-h-[56px] py-4 px-4 text-sm md:text-base placeholder:text-muted-foreground/60 scrollbar-hide"
                        rows={1}
                    />

                    <div className="flex items-center justify-between px-2 pb-2">
                        <div className="flex items-center gap-1">
                            <button className="p-2 rounded-xl text-muted-foreground hover:bg-background/50 hover:text-foreground transition-all">
                                <Paperclip size={18} />
                            </button>
                            <button className="p-2 rounded-xl text-muted-foreground hover:bg-background/50 hover:text-foreground transition-all">
                                <ImageIcon size={18} />
                            </button>
                        </div>

                        <div className="flex items-center gap-2">
                            <button className="p-2 rounded-xl text-muted-foreground hover:bg-background/50 hover:text-foreground transition-all">
                                <Mic size={18} />
                            </button>
                            <button
                                onClick={handleSend}
                                disabled={!content.trim() || isLoading}
                                className={clsx(
                                    "p-2.5 rounded-xl transition-all duration-300",
                                    content.trim() && !isLoading
                                        ? "bg-primary text-primary-foreground shadow-md shadow-primary/25 hover:scale-105"
                                        : "bg-muted text-muted-foreground cursor-not-allowed"
                                )}
                            >
                                <Send size={18} className={clsx(isLoading && "opacity-0")} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="text-center mt-3">
                <p className="text-xs text-muted-foreground">
                    AI can make mistakes. Please verify important information.
                </p>
            </div>
        </div>
    );
}
