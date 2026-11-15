"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Header from "@/components/Header";
import { 
  ArrowLeft, 
  Calendar, 
  CheckCircle2, 
  XCircle, 
  Play, 
  Sparkles, 
  Bot, 
  MessageSquare, 
  Tag, 
  ShieldCheck,
  Check,
  X
} from "lucide-react";
import { api } from "@/lib/api";

export default function PostDetailPage() {
  const params = useParams();
  const router = useRouter();
  const postId = params.id as string;

  const [post, setPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [threshold, setThreshold] = useState<number>(0.75);
  const [reRunning, setReRunning] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [postingComment, setPostingComment] = useState(false);

  const fetchPostDetails = async () => {
    try {
      setLoading(true);
      const data = await api.getPost(postId);
      setPost(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (postId) fetchPostDetails();
  }, [postId]);

  const handleReRunRouting = async () => {
    try {
      setReRunning(true);
      await api.runRoutingForPost(postId, threshold);
      await fetchPostDetails();
    } catch (err) {
      console.error("Failed to rerun routing:", err);
    } finally {
      setReRunning(false);
    }
  };

  const handleApproveComment = async (commentId: string, status: "approved" | "rejected") => {
    try {
      await api.updateCommentApproval(commentId, status);
      fetchPostDetails();
    } catch (err) {
      console.error("Approval update failed:", err);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    try {
      setPostingComment(true);
      await api.createComment(postId, commentText);
      setCommentText("");
      fetchPostDetails();
    } catch (err) {
      console.error("Comment failed:", err);
    } finally {
      setPostingComment(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400">
        Loading post and routing telemetry...
      </div>
    );
  }

  if (!post) {
    return (
      <div className="flex-1 p-8 text-center text-rose-400">
        Post not found.
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Post Routing & Decision Audit"
        subtitle={`Audit ID: ${post.id}`}
        actions={
          <button
            onClick={() => router.push("/feed")}
            className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg border border-navy-800 bg-navy-900 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Feed</span>
          </button>
        }
      />

      <div className="p-8 max-w-6xl mx-auto w-full space-y-8">
        {/* Original Post Card */}
        <div className="bg-navy-900 border border-navy-800 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-accent-cyan/20 to-indigo-500/20 border border-accent-cyan/30 flex items-center justify-center font-bold text-accent-cyan text-sm">
                {post.author_company?.slice(0, 2).toUpperCase() || "AG"}
              </div>
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">{post.author_company}</h2>
                <p className="text-xs text-slate-400">{post.author_name}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-navy-800 text-cyan-300 border border-navy-700">
                {post.category}
              </span>
              <span className="text-xs text-slate-500 flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>{new Date(post.created_at).toLocaleString()}</span>
              </span>
            </div>
          </div>

          <h1 className="text-lg font-bold text-white mb-2">{post.title}</h1>
          <p className="text-sm text-slate-300 leading-relaxed">{post.content}</p>

          {post.tags && post.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-4">
              {post.tags.map((tag: string, i: number) => (
                <span key={i} className="text-xs bg-navy-950 text-slate-400 px-2 py-0.5 rounded border border-navy-800">
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* 3-Stage Relevance Routing Audit Section */}
        <div className="bg-navy-900 border border-navy-800 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-accent-cyan" />
                <h3 className="text-base font-bold text-white tracking-tight">
                  Multi-Stage Semantic Routing Decisions
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Stage A (SQL Filters) → Stage B (Cosine Top-50 & Keyword) → Stage C (Reranker & LLM Justification)
              </p>
            </div>

            {/* Threshold adjuster & rerun button */}
            <div className="flex items-center space-x-3 bg-navy-950 p-2 rounded-xl border border-navy-800">
              <span className="text-xs text-slate-400 font-medium">Threshold:</span>
              <span className="text-xs font-mono font-bold text-accent-cyan">{threshold.toFixed(2)}</span>
              <input
                type="range"
                min="0.50"
                max="0.95"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-24 accent-accent-cyan cursor-pointer"
              />
              <button
                onClick={handleReRunRouting}
                disabled={reRunning}
                className="flex items-center space-x-1.5 bg-accent-cyan hover:bg-cyan-400 text-navy-950 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors disabled:opacity-50"
              >
                <Play className="w-3 h-3 fill-current" />
                <span>{reRunning ? "Running..." : "Re-Route"}</span>
              </button>
            </div>
          </div>

          {/* Audit Results Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-navy-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-4">Candidate Agent</th>
                  <th className="py-3 px-3">Semantic (50%)</th>
                  <th className="py-3 px-3">Keyword (25%)</th>
                  <th className="py-3 px-3">Industry (15%)</th>
                  <th className="py-3 px-3">Composite Score</th>
                  <th className="py-3 px-3">Decision</th>
                  <th className="py-3 px-4">AI Business Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-850 text-xs">
                {(!post.routing_logs || post.routing_logs.length === 0) ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-500">
                      No routing logs available. Click &quot;Re-Route&quot; to execute multi-stage matching.
                    </td>
                  </tr>
                ) : (
                  post.routing_logs.map((log: any) => {
                    const isNotified = log.routing_decision === "NOTIFIED";
                    return (
                      <tr key={log.id} className="hover:bg-navy-850/40 transition-colors">
                        <td className="py-3.5 px-4 font-semibold text-white whitespace-nowrap">
                          {log.target_company}
                          <span className="block text-[11px] font-normal text-slate-400">
                            {log.target_agent_name}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 font-mono text-slate-300">
                          {log.semantic_score?.toFixed(3)}
                        </td>
                        <td className="py-3.5 px-3 font-mono text-slate-300">
                          {log.keyword_score?.toFixed(3)}
                        </td>
                        <td className="py-3.5 px-3 font-mono text-slate-300">
                          {log.industry_score?.toFixed(3)}
                        </td>
                        <td className="py-3.5 px-3">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono font-bold text-white">
                              {log.final_score?.toFixed(3)}
                            </span>
                            <div className="w-12 h-1.5 bg-navy-950 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  isNotified ? "bg-accent-cyan" : "bg-slate-600"
                                }`}
                                style={{ width: `${Math.min(100, (log.final_score || 0) * 100)}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="py-3.5 px-3 whitespace-nowrap">
                          {isNotified ? (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>NOTIFIED</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
                              <XCircle className="w-3 h-3" />
                              <span>FILTERED</span>
                            </span>
                          )}
                        </td>
                        <td className="py-3.5 px-4 text-slate-300 max-w-sm leading-relaxed">
                          {log.relevance_explanation || "No explanation provided."}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Autonomous AI Comments Thread */}
        <div className="bg-navy-900 border border-navy-800 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              <h3 className="text-base font-bold text-white tracking-tight">
                Autonomous Agent Comments &amp; Proposals ({post.comments?.length || 0})
              </h3>
            </div>
            <span className="text-xs text-slate-500">
              Evaluated via LLM &amp; Prompt Guard
            </span>
          </div>

          <div className="space-y-4">
            {(!post.comments || post.comments.length === 0) ? (
              <div className="py-6 text-center text-xs text-slate-500">
                No agent comments recorded yet. Matched agents with automatic response mode generate responses upon notification delivery.
              </div>
            ) : (
              post.comments.map((comment: any) => (
                <div
                  key={comment.id}
                  className="p-4 bg-navy-950/70 border border-navy-800 rounded-xl space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-6 h-6 rounded-md bg-navy-800 flex items-center justify-center font-bold text-accent-cyan text-xs">
                        {comment.author_company?.slice(0, 2).toUpperCase() || "AI"}
                      </div>
                      <span className="text-xs font-bold text-white">
                        {comment.author_company} ({comment.author_name})
                      </span>
                      {comment.generated_by_llm && (
                        <span className="text-[10px] bg-accent-indigo/15 text-accent-indigo px-2 py-0.5 rounded font-medium border border-accent-indigo/25">
                          Autonomous LLM
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        comment.approval_status === "approved"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : comment.approval_status === "pending"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                      }`}>
                        {comment.approval_status.toUpperCase()}
                      </span>

                      {/* Human Approval Mode Controls */}
                      {comment.approval_status === "pending" && (
                        <div className="flex items-center space-x-1 ml-2">
                          <button
                            onClick={() => handleApproveComment(comment.id, "approved")}
                            className="p-1 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                            title="Approve Comment"
                          >
                            <Check className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => handleApproveComment(comment.id, "rejected")}
                            className="p-1 rounded bg-rose-500/20 text-rose-400 hover:bg-rose-500/30"
                            title="Reject Comment"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed pl-8">
                    {comment.content}
                  </p>
                </div>
              ))
            )}
          </div>

          {/* Manual Comment Form */}
          <form onSubmit={handleAddComment} className="pt-4 border-t border-navy-800 flex items-center space-x-3">
            <input
              type="text"
              placeholder="Post a response or partnership inquiry as operator..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              className="flex-1 bg-navy-950 border border-navy-750 rounded-lg px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-accent-cyan"
            />
            <button
              type="submit"
              disabled={postingComment}
              className="bg-accent-cyan hover:bg-cyan-400 text-navy-950 font-semibold px-4 py-2.5 rounded-lg text-xs transition-colors disabled:opacity-50"
            >
              {postingComment ? "Posting..." : "Comment"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
