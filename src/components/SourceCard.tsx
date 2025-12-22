"use client";

import React from "react";
import { FileText, ExternalLink } from "lucide-react";
import { motion } from "framer-motion";
import clsx from "clsx";

export interface Source {
    id: string;
    title: string;
    url?: string;
    snippet: string;
}

interface SourceCardProps {
    source: Source;
    index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
    return (
        <motion.div
            whileHover={{ y: -5, scale: 1.02 }}
            onClick={() => source.url && window.open(source.url, '_blank')}
            className={clsx(
                "flex flex-col gap-2 p-4 rounded-3xl liquid-glass border border-white/10 hover:border-white/20 transition-all group w-64 flex-shrink-0 shadow-xl",
                source.url ? "cursor-pointer" : "cursor-default"
            )}
        >
            <div className="flex items-center justify-between text-[11px] text-muted-foreground/60 mb-1 font-bold tracking-widest uppercase">
                <div className="flex items-center gap-2">
                    <FileText size={12} className="text-primary" />
                    <span>REF {index + 1}</span>
                </div>
                {source.url && <ExternalLink size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />}
            </div>

            <div className="font-semibold text-[14px] line-clamp-1 text-foreground leading-tight">
                {source.title}
            </div>

            <div className="text-[12px] text-muted-foreground line-clamp-2 leading-relaxed opacity-70">
                {source.snippet}
            </div>
        </motion.div>
    );
}
