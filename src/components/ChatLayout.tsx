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
      {/* Background Animated Mesh */}
      <div className="bg-mesh">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
        <div className="blob blob-3" />
      </div>

      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0, x: -20 }}
            animate={{ width: 300, opacity: 1, x: 0 }}
            exit={{ width: 0, opacity: 0, x: -20 }}
            transition={{ type: "spring", stiffness: 200, damping: 25 }}
            className="flex-shrink-0 h-full liquid-glass border-r border-white/10 relative z-20 m-4 rounded-[2.5rem] overflow-hidden"
          >
            <div className="flex flex-col h-full p-6">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3 font-semibold text-xl tracking-tight">
                  <div className="w-10 h-10 rounded-2xl bg-primary shadow-lg shadow-primary/30 flex items-center justify-center text-primary-foreground">
                    <MessageSquare size={22} />
                  </div>
                  <span>RAG AI</span>
                </div>
              </div>

              <button className="flex items-center justify-center gap-2 w-full py-4 rounded-2xl bg-white text-black hover:bg-white/90 transition-all shadow-xl active:scale-95 mb-8 font-semibold">
                <Plus size={20} strokeWidth={2.5} />
                <span>New Conversation</span>
              </button>

              <div className="space-y-2 mb-6">
                <div className="px-2 text-[11px] font-bold text-muted-foreground/60 mb-3 uppercase tracking-[0.1em]">
                  Recent Activity
                </div>
                {[1, 2, 3].map((i) => (
                  <button
                    key={i}
                    className="flex items-center gap-3 w-full p-3.5 rounded-2xl hover:bg-white/5 transition-all text-[13px] text-left group border border-transparent hover:border-white/5 active:scale-[0.98]"
                  >
                    <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-white/10">
                      <History size={14} className="text-muted-foreground group-hover:text-foreground transition-colors" />
                    </div>
                    <span className="truncate opacity-70 group-hover:opacity-100 font-medium">
                      Mechanism of deep learning...
                    </span>
                  </button>
                ))}
              </div>

              <div className="mt-auto pt-4">
                <button className="flex items-center gap-3 w-full p-3.5 rounded-2xl hover:bg-white/5 transition-all text-sm font-medium border border-transparent hover:border-white/5">
                  <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center">
                    <Settings size={18} className="text-muted-foreground" />
                  </div>
                  <span>System Settings</span>
                </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      <main className="flex-1 flex flex-col h-full relative z-10 p-4 pl-0">
        <div className="flex-1 flex flex-col liquid-glass border border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl relative">
          <header className="h-20 flex items-center justify-between px-8 border-b border-white/5 bg-white/5 backdrop-blur-md">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-3 rounded-2xl hover:bg-white/5 text-muted-foreground hover:text-foreground transition-all active:scale-90"
            >
              <PanelLeft size={22} />
            </button>

            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                <Search size={18} className="text-muted-foreground" />
              </div>
            </div>
          </header>

          <div className="flex-1 overflow-hidden relative">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
