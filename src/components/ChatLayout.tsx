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
import { DocumentSidebar } from "./DocumentSidebar";

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
            animate={{ width: 340, opacity: 1, x: 0 }}
            exit={{ width: 0, opacity: 0, x: -20 }}
            transition={{ type: "spring", stiffness: 200, damping: 25 }}
            className="flex-shrink-0 h-full relative z-20 m-4 overflow-hidden"
          >
            <DocumentSidebar />
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
