import React from "react";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  badge?: string;
  badgeColor?: "emerald" | "indigo" | "cyan" | "amber";
}

export default function MetricCard({
  label,
  value,
  subtext,
  icon: Icon,
  badge,
  badgeColor = "emerald"
}: MetricCardProps) {
  const badgeClasses = {
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    indigo: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    cyan: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  }[badgeColor];

  return (
    <div className="bg-navy-900/90 border border-navy-800 rounded-xl p-5 shadow-sm hover:border-navy-700 transition-all">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 tracking-wide uppercase">
          {label}
        </span>
        <div className="w-8 h-8 rounded-lg bg-navy-800 flex items-center justify-center text-slate-300">
          <Icon className="w-4 h-4 text-accent-cyan" />
        </div>
      </div>

      <div className="mt-4 flex items-baseline space-x-2">
        <span className="text-2xl font-bold tracking-tight text-white">
          {value}
        </span>
        {badge && (
          <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${badgeClasses}`}>
            {badge}
          </span>
        )}
      </div>

      {subtext && (
        <p className="mt-1 text-xs text-slate-400">
          {subtext}
        </p>
      )}
    </div>
  );
}
