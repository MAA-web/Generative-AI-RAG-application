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
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className={clsx(
                "flex w-full mb-10",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            <div className={clsx(
                "flex max-w-[85%] md:max-w-[75%] gap-5",
                isUser ? "flex-row-reverse" : "flex-row"
            )}>
                {/* Avatar */}
                <div className={clsx(
                    "flex-shrink-0 w-11 h-11 rounded-[1.25rem] flex items-center justify-center border shadow-xl relative overflow-hidden",
                    isUser
                        ? "bg-primary text-primary-foreground border-white/20"
                        : "liquid-glass text-foreground border-white/10"
                )}>
                    {isUser ? <User size={20} /> : <Bot size={20} />}
                    {!isUser && <div className="absolute inset-0 bg-primary/10 animate-pulse" />}
                </div>

                {/* Content */}
                <div className={clsx(
                    "flex flex-col gap-2",
                    isUser ? "items-end" : "items-start"
                )}>
                    <div className={clsx(
                        "relative px-7 py-5 rounded-[2rem] shadow-2xl text-[15px] md:text-[16px] leading-[1.6] whitespace-pre-wrap font-medium tracking-tight",
                        isUser
                            ? "bg-primary text-secondary-foreground rounded-tr-[0.5rem]"
                            : "liquid-glass-vibrant border border-white/20 text-foreground rounded-tl-[0.5rem]"
                    )}>
                        {message.content}
                    </div>

                    {/* Actions (AI only) */}
                    {!isUser && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex items-center gap-1 mt-1 ml-2"
                        >
                            <button className="p-2 rounded-xl text-muted-foreground hover:bg-white/5 hover:text-foreground transition-all">
                                <Copy size={15} />
                            </button>
                            <button className="p-2 rounded-xl text-muted-foreground hover:bg-white/5 hover:text-foreground transition-all">
                                <ThumbsUp size={15} />
                            </button>
                            <button className="p-2 rounded-xl text-muted-foreground hover:bg-white/5 hover:text-foreground transition-all">
                                <ThumbsDown size={15} />
                            </button>
                        </motion.div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
