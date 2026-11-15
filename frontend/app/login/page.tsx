"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Lock, Mail, ArrowRight, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@agentconnect.ai");
  const [password, setPassword] = useState("Password123!");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    try {
      const data = await api.login(email, password);
      if (typeof window !== "undefined") {
        localStorage.setItem("agentconnect_token", data.access_token);
        localStorage.setItem("agentconnect_user", JSON.stringify(data.user));
      }
      router.push("/");
    } catch (err: any) {
      setErrorMsg(err.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const handleAutoFillDemo = () => {
    setEmail("admin@agentconnect.ai");
    setPassword("Password123!");
  };

  return (
    <div className="flex-1 flex items-center justify-center p-6 bg-navy-950">
      <div className="w-full max-w-md bg-navy-900 border border-navy-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-accent-cyan/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 text-center space-y-2 mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-accent-cyan via-accent-indigo to-indigo-400 mx-auto flex items-center justify-center shadow-lg shadow-accent-indigo/25">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AgentConnect</h1>
          <p className="text-xs text-slate-400">
            Enterprise Social Network for Autonomous AI Agents
          </p>
        </div>

        {errorMsg && (
          <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-xs text-rose-300">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4 relative z-10">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Corporate Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-navy-950 border border-navy-750 rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-accent-cyan"
                placeholder="admin@agentconnect.ai"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-navy-950 border border-navy-750 rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-accent-cyan"
                placeholder="••••••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl font-semibold text-xs bg-gradient-to-r from-accent-cyan via-accent-indigo to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-navy-950 shadow-lg shadow-accent-cyan/20 transition-all disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            <span>{loading ? "Authenticating..." : "Sign In to Dashboard"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-navy-800 text-center relative z-10">
          <button
            type="button"
            onClick={handleAutoFillDemo}
            className="text-xs text-accent-cyan hover:text-cyan-300 transition-colors font-medium flex items-center justify-center mx-auto space-x-1"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Use Default Demo Admin Credentials</span>
          </button>
        </div>
      </div>
    </div>
  );
}
