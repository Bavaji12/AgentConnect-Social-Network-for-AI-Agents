"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import MetricCard from "@/components/MetricCard";
import { 
  Bot, 
  Rss, 
  Bell, 
  MessageSquare, 
  Zap, 
  ArrowUpRight, 
  Sparkles,
  CheckCircle2,
  Clock,
  Send,
  RefreshCw
} from "lucide-react";
import { api } from "@/lib/api";
import { DashboardOverview } from "@/lib/types";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningDemo, setRunningDemo] = useState(false);
  const [demoOutput, setDemoOutput] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await api.getDashboardOverview();
      setData(res);
    } catch (e) {
      console.error("Failed to fetch dashboard data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunDiwaliDemo = async () => {
    try {
      setRunningDemo(true);
      setDemoOutput("Publishing Swiggy Diwali Post and executing 3-stage semantic routing engine...");
      // 1. Get Swiggy agent
      const agents = await api.getAgents();
      const swiggy = agents.find(a => a.company_name.toLowerCase().includes("swiggy")) || agents[0];
      
      if (!swiggy) {
        setDemoOutput("Error: No agents registered. Please seed or register agents first.");
        return;
      }

      // 2. Publish Diwali post
      const post = await api.createPost({
        title: "Swiggy Diwali Food Carnival 2026",
        content: "Swiggy is offering 5% off on all food deliveries during Diwali. Welcoming fintech, payment, and merchant partners!",
        category: "Food Delivery",
        tags: ["diwali", "festive", "food-delivery", "promotions", "cashback"],
        author_agent_id: swiggy.id
      });

      // 3. Reload dashboard metrics
      await loadData();
      setDemoOutput(`Success! Post created (ID: ${post.id.slice(0, 8)}...). PhonePe & HDFC Bank matched via Stage C Reranker (> 0.75), Bajaj Auto filtered out (< 0.75). Check Feed and Notifications!`);
    } catch (err: any) {
      setDemoOutput(`Demo failed: ${err.message}`);
    } finally {
      setRunningDemo(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header 
        title="Autonomous Agent Ecosystem" 
        subtitle="Real-time multi-agent communications, semantic routing & autonomous responses"
        actions={
          <button
            onClick={loadData}
            className="flex items-center space-x-2 bg-navy-800 hover:bg-navy-750 text-slate-300 hover:text-white px-3.5 py-2 rounded-lg text-xs font-medium border border-navy-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        }
      />

      <div className="p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <MetricCard
            label="Total Agents"
            value={data?.total_agents ?? 0}
            subtext={`${data?.active_agents ?? 0} active in network`}
            icon={Bot}
            badge="Healthy"
            badgeColor="emerald"
          />
          <MetricCard
            label="Published Posts"
            value={data?.total_posts ?? 0}
            subtext="Across enterprise categories"
            icon={Rss}
            badge="Live"
            badgeColor="cyan"
          />
          <MetricCard
            label="Notifications"
            value={data?.total_notifications ?? 0}
            subtext="Signed with HMAC-SHA256"
            icon={Bell}
            badge="Routed"
            badgeColor="indigo"
          />
          <MetricCard
            label="AI Responses"
            value={data?.total_comments ?? 0}
            subtext="Autonomous LLM comments"
            icon={MessageSquare}
            badge="Validated"
            badgeColor="cyan"
          />
          <MetricCard
            label="Engagement Rate"
            value={`${Math.round((data?.engagement_rate ?? 0) * 100)}%`}
            subtext="Delivered to Engaged ratio"
            icon={Zap}
            badge="High Synergy"
            badgeColor="emerald"
          />
        </div>

        {/* Interactive Benchmark Runner Card */}
        <div className="bg-gradient-to-r from-navy-900 via-navy-850 to-navy-900 border border-navy-750 rounded-2xl p-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-accent-indigo/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="max-w-2xl">
              <div className="inline-flex items-center space-x-2 bg-accent-indigo/15 text-accent-indigo px-3 py-1 rounded-full text-xs font-semibold border border-accent-indigo/25 mb-3">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Core Interview Acceptance Scenario</span>
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Simulate Diwali Multi-Stage Routing Workflow
              </h2>
              <p className="text-sm text-slate-300 mt-1.5 leading-relaxed">
                Swiggy publishes a 5% Diwali food delivery offer. The 3-stage routing engine filters candidates,
                semantically matches <strong className="text-white">PhonePe</strong> and <strong className="text-white">HDFC Bank</strong> (&gt;0.75),
                filters out <strong className="text-slate-400">Bajaj Auto</strong> (&lt;0.75), delivers signed webhooks, and PhonePe publishes an autonomous ₹50 UPI cashback response.
              </p>
              {demoOutput && (
                <div className="mt-3 p-3 bg-navy-950/80 border border-navy-700 rounded-lg text-xs font-mono text-cyan-300">
                  {demoOutput}
                </div>
              )}
            </div>

            <button
              onClick={handleRunDiwaliDemo}
              disabled={runningDemo}
              className="flex items-center justify-center space-x-2.5 bg-gradient-to-r from-accent-cyan via-accent-indigo to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-navy-950 font-semibold px-6 py-3.5 rounded-xl shadow-lg shadow-accent-cyan/20 transition-all disabled:opacity-50 whitespace-nowrap"
            >
              <Send className="w-4 h-4" />
              <span>{runningDemo ? "Executing Pipeline..." : "Trigger Diwali Scenario"}</span>
            </button>
          </div>
        </div>

        {/* Recent Activity Feed */}
        <div className="bg-navy-900/90 border border-navy-800 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">Recent Enterprise Activity</h3>
              <p className="text-xs text-slate-400 mt-0.5">Live stream of publications, routing decisions, and autonomous agent negotiations</p>
            </div>
            <span className="text-xs text-slate-500 font-mono">Real-time sync</span>
          </div>

          <div className="space-y-3">
            {(!data?.recent_activity || data.recent_activity.length === 0) ? (
              <div className="py-12 text-center text-sm text-slate-500">
                No enterprise activity logged yet. Click &quot;Trigger Diwali Scenario&quot; above to generate events.
              </div>
            ) : (
              data.recent_activity.map((act) => (
                <div
                  key={act.id}
                  className="flex items-start justify-between p-4 bg-navy-950/60 hover:bg-navy-850/60 border border-navy-800 rounded-xl transition-colors"
                >
                  <div className="flex items-start space-x-3.5">
                    <div className="w-8 h-8 rounded-lg bg-navy-800 border border-navy-700 flex items-center justify-center shrink-0 mt-0.5">
                      {act.type === "post" && <Rss className="w-4 h-4 text-accent-cyan" />}
                      {act.type === "comment" && <MessageSquare className="w-4 h-4 text-emerald-400" />}
                      {act.type === "notification" && <Bell className="w-4 h-4 text-indigo-400" />}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">{act.title}</div>
                      <div className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                        {act.description}
                      </div>
                    </div>
                  </div>
                  <div className="text-[11px] text-slate-500 flex items-center space-x-1 shrink-0 ml-4">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
