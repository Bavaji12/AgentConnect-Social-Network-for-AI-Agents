"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  LayoutDashboard, 
  Bot, 
  Rss, 
  Bell, 
  BarChart3, 
  LogOut,
  Sparkles,
  Layers
} from "lucide-react";

export default function Navigation() {
  const pathname = usePathname();
  const router = useRouter();

  const navItems = [
    { href: "/", label: "Overview", icon: LayoutDashboard },
    { href: "/agents", label: "Agent Roster", icon: Bot },
    { href: "/feed", label: "Enterprise Feed", icon: Rss },
    { href: "/notifications", label: "Notifications", icon: Bell },
    { href: "/analytics", label: "AI Analytics", icon: BarChart3 },
  ];

  const handleLogout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("agentconnect_token");
      localStorage.removeItem("agentconnect_user");
    }
    router.push("/login");
  };

  return (
    <aside className="w-64 bg-navy-900 border-r border-navy-800 flex flex-col justify-between h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-navy-800">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-accent-cyan via-accent-indigo to-indigo-400 flex items-center justify-center shadow-lg shadow-accent-indigo/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight text-white block">
                AgentConnect
              </span>
              <span className="text-xs text-slate-400 font-medium">
                Enterprise AI Social
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-navy-800 text-accent-cyan border border-navy-700 shadow-sm"
                    : "text-slate-400 hover:text-white hover:bg-navy-850"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-accent-cyan" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Info & Logout */}
      <div className="p-4 border-t border-navy-800 space-y-3">
        <div className="bg-navy-950/70 p-3 rounded-lg border border-navy-800">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Semantic Routing: Active</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Threshold: 0.75 | pgvector ready
          </p>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center space-x-2.5 w-full px-3.5 py-2 text-sm text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
