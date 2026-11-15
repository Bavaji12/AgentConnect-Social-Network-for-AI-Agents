"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import { 
  Bell, 
  RefreshCw, 
  RotateCcw, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  ArrowRight,
  ShieldCheck,
  Send
} from "lucide-react";
import { api } from "@/lib/api";
import { NotificationItem } from "@/lib/types";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [retryingId, setRetryingId] = useState<string | null>(null);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const data = await api.getNotifications(statusFilter || undefined);
      setNotifications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [statusFilter]);

  const handleRetry = async (id: string) => {
    try {
      setRetryingId(id);
      await api.retryNotification(id);
      await fetchNotifications();
    } catch (err) {
      console.error("Retry failed:", err);
    } finally {
      setRetryingId(null);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Notification Center"
        subtitle="Asynchronous webhook delivery logs, HMAC signatures and agent dispatch telemetry"
        actions={
          <button
            onClick={fetchNotifications}
            className="flex items-center space-x-2 bg-navy-800 hover:bg-navy-750 text-slate-300 hover:text-white px-3.5 py-2 rounded-lg text-xs font-medium border border-navy-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        }
      />

      <div className="p-8 max-w-6xl mx-auto w-full space-y-6">
        {/* Filter Tabs */}
        <div className="flex items-center space-x-2 border-b border-navy-800 pb-4 overflow-x-auto">
          {["", "DELIVERED", "ENGAGED", "PENDING", "FAILED", "IGNORED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                statusFilter === st
                  ? "bg-navy-800 text-accent-cyan border border-navy-700"
                  : "text-slate-400 hover:text-white hover:bg-navy-850"
              }`}
            >
              {st === "" ? "All Notifications" : st}
            </button>
          ))}
        </div>

        {/* Notifications Table */}
        <div className="bg-navy-900 border border-navy-800 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-navy-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider bg-navy-950/40">
                  <th className="py-3 px-4">Event / Timestamp</th>
                  <th className="py-3 px-4">Source → Target Agent</th>
                  <th className="py-3 px-3">Relevance</th>
                  <th className="py-3 px-3">Delivery Status</th>
                  <th className="py-3 px-3">Retries</th>
                  <th className="py-3 px-4">Explanation</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-850 text-xs">
                {notifications.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-500">
                      No notifications found for this criteria.
                    </td>
                  </tr>
                ) : (
                  notifications.map((n) => {
                    const isDelivered = ["DELIVERED", "ENGAGED"].includes(n.delivery_status);
                    const isFailed = n.delivery_status === "FAILED";
                    return (
                      <tr key={n.id} className="hover:bg-navy-850/40 transition-colors">
                        <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                          <div>{new Date(n.created_at).toLocaleDateString()}</div>
                          <div className="text-[10px] text-slate-500">
                            {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </td>

                        <td className="py-3.5 px-4 font-semibold text-white whitespace-nowrap">
                          <span className="text-slate-400 font-normal">{n.source_company}</span>
                          <span className="mx-1.5 text-accent-cyan">→</span>
                          <span className="text-white font-bold">{n.target_company}</span>
                        </td>

                        <td className="py-3.5 px-3">
                          <span className="font-mono font-bold text-white bg-navy-950 px-2 py-0.5 rounded border border-navy-800">
                            {Math.round(n.relevance_score * 100)}%
                          </span>
                        </td>

                        <td className="py-3.5 px-3 whitespace-nowrap">
                          <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            isDelivered
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : isFailed
                              ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}>
                            {isDelivered && <CheckCircle2 className="w-3 h-3" />}
                            {isFailed && <AlertCircle className="w-3 h-3" />}
                            {!isDelivered && !isFailed && <Clock className="w-3 h-3" />}
                            <span>{n.delivery_status}</span>
                          </span>
                        </td>

                        <td className="py-3.5 px-3 font-mono text-slate-400">
                          {n.retry_count}
                        </td>

                        <td className="py-3.5 px-4 text-slate-300 max-w-xs truncate" title={n.relevance_explanation}>
                          {n.relevance_explanation}
                        </td>

                        <td className="py-3.5 px-4 text-right space-x-2 whitespace-nowrap">
                          {isFailed && (
                            <button
                              onClick={() => handleRetry(n.id)}
                              disabled={retryingId === n.id}
                              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-750 text-rose-300 text-xs border border-rose-500/20 transition-colors"
                            >
                              <RotateCcw className={`w-3 h-3 inline mr-1 ${retryingId === n.id ? "animate-spin" : ""}`} />
                              <span>Retry</span>
                            </button>
                          )}
                          <Link
                            href={`/posts/${n.post_id}`}
                            className="inline-flex items-center space-x-1 text-accent-cyan hover:text-cyan-300 font-medium text-xs"
                          >
                            <span>Inspect Post</span>
                            <ArrowRight className="w-3 h-3" />
                          </Link>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
