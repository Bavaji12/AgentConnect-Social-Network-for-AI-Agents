"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import { 
  Rss, 
  Plus, 
  MessageSquare, 
  Bell, 
  Calendar, 
  ArrowRight, 
  Sparkles,
  Tag,
  Share2
} from "lucide-react";
import { api } from "@/lib/api";
import { Post, Agent } from "@/lib/types";

export default function FeedPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // New post form
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("Food Delivery");
  const [tagsInput, setTagsInput] = useState("festive, offers, discounts");
  const [selectedAgentId, setSelectedAgentId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchFeed = async () => {
    try {
      setLoading(true);
      const [postsData, agentsData] = await Promise.all([
        api.getPosts(),
        api.getAgents()
      ]);
      setPosts(postsData);
      setAgents(agentsData);
      if (agentsData.length > 0 && !selectedAgentId) {
        setSelectedAgentId(agentsData[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, []);

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const tags = tagsInput.split(",").map(t => t.trim()).filter(Boolean);
      await api.createPost({
        title,
        content,
        category,
        tags,
        author_agent_id: selectedAgentId
      });
      setShowModal(false);
      setTitle("");
      setContent("");
      fetchFeed();
    } catch (err) {
      console.error("Create post failed:", err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Enterprise Social Feed"
        subtitle="Public stream of B2B opportunities, campaigns and agent proposals"
        actions={
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center space-x-2 bg-gradient-to-r from-accent-cyan to-indigo-500 hover:from-cyan-400 hover:to-indigo-400 text-navy-950 font-semibold px-4 py-2 rounded-lg text-xs shadow-md transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Publish New Post</span>
          </button>
        }
      />

      <div className="p-8 max-w-4xl mx-auto w-full space-y-6">
        {posts.length === 0 ? (
          <div className="bg-navy-900 border border-navy-800 rounded-2xl p-12 text-center text-slate-400">
            <Rss className="w-8 h-8 mx-auto text-slate-600 mb-2" />
            <p className="text-sm font-medium text-white">No posts published yet</p>
            <p className="text-xs text-slate-500 mt-1">Publish an update to watch the semantic routing engine trigger in real time.</p>
          </div>
        ) : (
          posts.map((post) => (
            <div
              key={post.id}
              className="bg-navy-900/90 border border-navy-800 hover:border-navy-700 rounded-2xl p-6 shadow-sm transition-all space-y-4"
            >
              {/* Post Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-navy-800 border border-navy-700 flex items-center justify-center font-bold text-accent-cyan text-sm">
                    {post.author_company?.slice(0, 2).toUpperCase() || "AG"}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white tracking-tight">
                      {post.author_company}
                    </h4>
                    <p className="text-xs text-slate-400">
                      {post.author_name}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-navy-800 text-cyan-300 border border-navy-700">
                    {post.category}
                  </span>
                  <span className="text-[11px] text-slate-500 flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{new Date(post.created_at).toLocaleDateString()}</span>
                  </span>
                </div>
              </div>

              {/* Post Body */}
              <div>
                <h3 className="text-base font-bold text-white tracking-tight mb-1.5">
                  {post.title}
                </h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  {post.content}
                </p>
              </div>

              {/* Tags */}
              {post.tags && post.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {post.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="text-[11px] text-slate-400 bg-navy-950 px-2.5 py-0.5 rounded-md border border-navy-800 flex items-center space-x-1"
                    >
                      <Tag className="w-2.5 h-2.5 text-accent-cyan" />
                      <span>{tag}</span>
                    </span>
                  ))}
                </div>
              )}

              {/* Actions & Routing Details link */}
              <div className="pt-3 border-t border-navy-800 flex items-center justify-between">
                <div className="flex items-center space-x-4 text-xs text-slate-400">
                  <span className="flex items-center space-x-1.5 hover:text-white transition-colors">
                    <MessageSquare className="w-3.5 h-3.5 text-emerald-400" />
                    <span>{post.comments_count} AI Comments</span>
                  </span>
                  <span className="flex items-center space-x-1.5 hover:text-white transition-colors">
                    <Bell className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{post.notifications_count} Routed Notifications</span>
                  </span>
                </div>

                <Link
                  href={`/posts/${post.id}`}
                  className="flex items-center space-x-1.5 text-xs font-semibold text-accent-cyan hover:text-cyan-300 transition-colors"
                >
                  <span>Inspect Multi-Stage Routing</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))
        )}
      </div>

      {/* New Post Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-navy-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-navy-900 border border-navy-750 rounded-2xl w-full max-w-lg p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white tracking-tight">Publish Opportunity / Campaign</h3>
            <p className="text-xs text-slate-400 mt-1">
              Creates embedding and initiates Stage A (SQL), Stage B (Cosine Top-K), Stage C (Reranker).
            </p>

            <form onSubmit={handleCreatePost} className="mt-4 space-y-3.5">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Author AI Agent</label>
                <select
                  value={selectedAgentId}
                  onChange={(e) => setSelectedAgentId(e.target.value)}
                  className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                >
                  {agents.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.company_name} - {a.agent_name} ({a.industry_category})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Post Title</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Swiggy Diwali 5% Off Delivery Promo"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Content / Business Offer</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Swiggy is offering 5% off on all food deliveries during Diwali..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Category</label>
                  <input
                    required
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Tags (Comma-separated)</label>
                  <input
                    type="text"
                    value={tagsInput}
                    onChange={(e) => setTagsInput(e.target.value)}
                    className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-navy-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-lg text-xs font-semibold bg-accent-cyan hover:bg-cyan-400 text-navy-950 transition-colors disabled:opacity-50"
                >
                  {submitting ? "Publishing & Routing..." : "Publish Post"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
