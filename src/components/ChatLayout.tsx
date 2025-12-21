"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  MessageSquare, 
  Settings, 
  Menu, 
  Plus, 
  Search,
  History,
  PanelLeft
} from "lucide-react";
import clsx from "clsx";

interface ChatLayoutProps {
  children: React.ReactNode;
}

export function ChatLayout({ children }: ChatLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground relative">
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="flex-shrink-0 h-full border-r border-border bg-card/50 backdrop-blur-xl relative z-20"
          >
            <div className="flex flex-col h-full p-4">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2 font-semibold text-lg">
                  <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
                    <MessageSquare size={18} />
                  </div>
                  <span>RAG Chat</span>
                </div>
              </div>

              <button className="flex items-center gap-2 w-full p-3 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20 mb-6">
                <Plus size={18} />
                <span className="font-medium">New Chat</span>
              </button>

              <div className="space-y-1 mb-6">
                <div className="px-2 text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">
                  Recent
                </div>
                {[1, 2, 3].map((i) => (
                  <button
                    key={i}
                    className="flex items-center gap-3 w-full p-2.5 rounded-lg hover:bg-white/5 transition-colors text-sm text-left group"
                  >
                    <History size={16} className="text-muted-foreground group-hover:text-foreground transition-colors" />
                    <span className="truncate opacity-80 group-hover:opacity-100">
                      Query about photosynthesis mechanism...
                    </span>
                  </button>
                ))}
              </div>

              <div className="mt-auto pt-4 border-t border-border">
                  <button className="flex items-center gap-3 w-full p-2.5 rounded-lg hover:bg-white/5 transition-colors text-sm text-left">
                    <Settings size={18} className="text-muted-foreground" />
                    <span>Settings</span>
                  </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      <main className="flex-1 flex flex-col h-full relative z-10">
        <header className="h-16 flex items-center justify-between px-6 border-b border-border/40 bg-background/50 backdrop-blur-sm">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 rounded-lg hover:bg-white/5 text-muted-foreground hover:text-foreground transition-colors"
          >
            <PanelLeft size={20} />
          </button>
          
          <div className="flex items-center gap-4">
             {/* Header actions can go here */}
          </div>
        </header>
        
        <div className="flex-1 overflow-hidden relative">
          {children}
        </div>
      </main>
    </div>
  );
}
