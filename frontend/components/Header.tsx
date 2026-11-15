"use client";

import { Bell, Sparkles } from "lucide-react";

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export default function Header({ title, subtitle, actions }: HeaderProps) {
  return (
    <header className="bg-navy-900/60 backdrop-blur-md border-b border-navy-800 px-8 py-5 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">{title}</h1>
        {subtitle && (
          <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {actions}
        <div className="flex items-center space-x-2 bg-navy-850 px-3 py-1.5 rounded-full border border-navy-750 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="font-medium text-emerald-400">PostgreSQL + pgvector</span>
        </div>
      </div>
    </header>
  );
}
