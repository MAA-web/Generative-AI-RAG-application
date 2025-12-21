"use client";

import React from "react";
import { motion } from "framer-motion";
import { User, Bot, Copy, ThumbsUp, ThumbsDown, MoreHorizontal } from "lucide-react";
import clsx from "clsx";

export interface Message {
    id: string;
    role: "user" | "ai";
    content: string;
    timestamp?: string;
    isThinking?: boolean;
}

interface MessageItemProps {
    message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
    const isUser = message.role === "user";

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className={clsx(
                "flex w-full mb-8",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            <div className={clsx(
                "flex max-w-[80%] md:max-w-[70%] gap-4",
                isUser ? "flex-row-reverse" : "flex-row"
            )}>
                {/* Avatar */}
                <div className={clsx(
                    "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border shadow-sm",
                    isUser
                        ? "bg-primary text-primary-foreground border-primary/20"
                        : "bg-card text-foreground border-border"
                )}>
                    {isUser ? <User size={18} /> : <Bot size={18} />}
                </div>

                {/* Content */}
                <div className={clsx(
                    "flex flex-col",
                    isUser ? "items-end" : "items-start"
                )}>
                    <div className={clsx(
                        "relative px-6 py-4 rounded-2xl shadow-sm text-sm md:text-base leading-relaxed whitespace-pre-wrap",
                        isUser
                            ? "bg-primary text-primary-foreground rounded-tr-sm"
                            : "bg-card border border-border text-foreground rounded-tl-sm glass"
                    )}>
                        {message.content}
                    </div>

                    {/* Actions (AI only) */}
                    {!isUser && (
                        <div className="flex items-center gap-2 mt-2 ml-1">
                            <button className="p-1.5 rounded-md text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors">
                                <Copy size={14} />
                            </button>
                            <button className="p-1.5 rounded-md text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors">
                                <ThumbsUp size={14} />
                            </button>
                            <button className="p-1.5 rounded-md text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors">
                                <ThumbsDown size={14} />
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
