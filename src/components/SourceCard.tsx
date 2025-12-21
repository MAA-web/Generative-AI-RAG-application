"use client";

import React from "react";
import { FileText, ExternalLink } from "lucide-react";

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
        <div className="flex flex-col gap-2 p-3 rounded-lg bg-secondary/50 border border-border/50 hover:bg-secondary hover:border-border transition-all cursor-pointer group w-60 flex-shrink-0">
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                <div className="flex items-center gap-1.5">
                    <FileText size={12} />
                    <span className="font-mono">SOURCE {index + 1}</span>
                </div>
                {source.url && <ExternalLink size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />}
            </div>

            <div className="font-medium text-sm line-clamp-1 text-foreground">
                {source.title}
            </div>

            <div className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                {source.snippet}
            </div>
        </div>
    );
}
