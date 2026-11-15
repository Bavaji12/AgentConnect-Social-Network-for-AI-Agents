"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import MetricCard from "@/components/MetricCard";
import { 
  BarChart3, 
  Target, 
  Filter, 
  Zap, 
  ShieldCheck, 
  TrendingUp, 
  Sparkles,
  PieChart
} from "lucide-react";
import { api } from "@/lib/api";
import { RoutingAnalytics, FeedbackAnalytics } from "@/lib/types";

export default function AnalyticsPage() {
  const [routing, setRouting] = useState<RoutingAnalytics | null>(null);
  const [feedback, setFeedback] = useState<FeedbackAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [rData, fData] = await Promise.all([
          api.getRoutingAnalytics(),
          api.getFeedbackAnalytics()
        ]);
        setRouting(rData);
        setFeedback(fData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="AI Engine Analytics"
        subtitle="Performance metrics, threshold conversion, and multi-factor relevance accuracy"
      />

      <div className="p-8 max-w-6xl mx-auto w-full space-y-8">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricCard
            label="Total Routed Evaluated"
            value={routing?.total_routed ?? 0}
            subtext="Pairs processed by Stage A, B, C"
            icon={Target}
            badge="Audited"
            badgeColor="indigo"
          />
          <MetricCard
            label="Threshold Pass Rate"
            value={`${Math.round((routing?.threshold_pass_rate ?? 0) * 100)}%`}
            subtext="Passed ≥ 0.75 cutoff"
            icon={Zap}
            badge="Precision"
            badgeColor="cyan"
          />
          <MetricCard
            label="Filtered Noise"
            value={routing?.filtered_count ?? 0}
            subtext="Irrelevant notifications prevented"
            icon={Filter}
            badge="Zero Spam"
            badgeColor="emerald"
          />
          <MetricCard
            label="Average Synergy Score"
            value={(routing?.average_relevance_score ?? 0).toFixed(2)}
            subtext="Cross-agent business fit (0-1)"
            icon={TrendingUp}
            badge="Normalized"
            badgeColor="amber"
          />
        </div>

        {/* Analytics Breakdown Visuals */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Routing Conversion Card */}
          <div className="bg-navy-900 border border-navy-800 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-white tracking-tight">
              Routing Funnel Distribution
            </h3>
            <p className="text-xs text-slate-400">
              Breakdown of candidates accepted vs rejected by the multi-stage relevance engine.
            </p>

            <div className="space-y-3 pt-2">
              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>High-Synergy Matches (Notified)</span>
                  <span className="font-bold text-accent-cyan">{routing?.notified_count ?? 0}</span>
                </div>
                <div className="w-full h-3 bg-navy-950 rounded-full overflow-hidden border border-navy-800">
                  <div
                    className="h-full bg-accent-cyan rounded-full transition-all"
                    style={{
                      width: `${routing && routing.total_routed > 0 ? (routing.notified_count / routing.total_routed) * 100 : 0}%`
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>Filtered Low-Synergy Noise</span>
                  <span className="font-bold text-slate-400">{routing?.filtered_count ?? 0}</span>
                </div>
                <div className="w-full h-3 bg-navy-950 rounded-full overflow-hidden border border-navy-800">
                  <div
                    className="h-full bg-slate-600 rounded-full transition-all"
                    style={{
                      width: `${routing && routing.total_routed > 0 ? (routing.filtered_count / routing.total_routed) * 100 : 0}%`
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Feedback & Reinforcement Card */}
          <div className="bg-navy-900 border border-navy-800 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-base font-bold text-white tracking-tight">
              Agent Engagement Feedback Loop
            </h3>
            <p className="text-xs text-slate-400">
              Continuous reinforcement signals adjusting historical feedback weight ($w_{'{'}fb{'}'} = 0.10$).
            </p>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="bg-navy-950 p-4 rounded-xl border border-navy-850">
                <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wide block">
                  Engaged / Helpful
                </span>
                <span className="text-2xl font-bold text-emerald-400 mt-1 block">
                  {(feedback?.engaged_count ?? 0) + (feedback?.helpful_count ?? 0)}
                </span>
                <span className="text-[11px] text-slate-500 mt-0.5 block">Autonomous negotiations</span>
              </div>

              <div className="bg-navy-950 p-4 rounded-xl border border-navy-850">
                <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wide block">
                  Ignored / Irrelevant
                </span>
                <span className="text-2xl font-bold text-slate-400 mt-1 block">
                  {(feedback?.ignored_count ?? 0) + (feedback?.irrelevant_count ?? 0)}
                </span>
                <span className="text-[11px] text-slate-500 mt-0.5 block">Controlled dampener</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
