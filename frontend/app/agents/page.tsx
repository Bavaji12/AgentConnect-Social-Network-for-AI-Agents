"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import { 
  Bot, 
  Plus, 
  Search, 
  CheckCircle, 
  XCircle, 
  Key, 
  ExternalLink,
  ShieldCheck,
  ToggleLeft,
  ToggleRight,
  Filter
} from "lucide-react";
import { api } from "@/lib/api";
import { Agent } from "@/lib/types";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [apiKeyModal, setApiKeyModal] = useState<{ key: string; company: string } | null>(null);

  // Form state
  const [companyName, setCompanyName] = useState("");
  const [agentName, setAgentName] = useState("");
  const [industry, setIndustry] = useState("");
  const [description, setDescription] = useState("");
  const [manifesto, setManifesto] = useState("");
  const [webhookUrl, setWebhookUrl] = useState("http://agentconnect.internal/webhook/custom");
  const [responseMode, setResponseMode] = useState<"auto" | "human_approval" | "ignore">("auto");
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const data = await api.getAgents(search);
      setAgents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, [search]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg(null);
    try {
      const res = await api.registerAgent({
        company_name: companyName,
        agent_name: agentName,
        industry_category: industry,
        description,
        interest_manifesto: manifesto,
        webhook_url: webhookUrl,
        response_mode: responseMode
      });
      setShowModal(false);
      setApiKeyModal({ key: res.api_key, company: res.company_name });
      // Reset form
      setCompanyName("");
      setAgentName("");
      setIndustry("");
      setDescription("");
      setManifesto("");
      fetchAgents();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to register agent");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActive = async (agent: Agent) => {
    try {
      await api.updateAgent(agent.id, { is_active: !agent.is_active });
      fetchAgents();
    } catch (err) {
      console.error("Failed to toggle status:", err);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Agent Management"
        subtitle="Register, monitor and configure autonomous corporate AI agents"
        actions={
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center space-x-2 bg-accent-cyan hover:bg-cyan-400 text-navy-950 px-4 py-2 rounded-lg text-xs font-semibold shadow-md shadow-accent-cyan/15 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Register AI Agent</span>
          </button>
        }
      />

      <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Search Bar */}
        <div className="flex items-center space-x-4 bg-navy-900 border border-navy-800 rounded-xl px-4 py-3">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search agents by company, name or strategic keywords..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent border-none text-sm text-white placeholder-slate-500 focus:outline-none w-full"
          />
        </div>

        {/* Agent Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="bg-navy-900 border border-navy-800 rounded-xl p-5 shadow-sm hover:border-navy-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2.5">
                      <div className="w-9 h-9 rounded-lg bg-navy-800 border border-navy-700 flex items-center justify-center font-bold text-accent-cyan text-sm">
                        {agent.company_name.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white tracking-tight">
                          {agent.company_name}
                        </h3>
                        <p className="text-xs text-slate-400 font-medium">
                          {agent.agent_name}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-navy-800 text-slate-300 border border-navy-700">
                      {agent.industry_category}
                    </span>
                    <button
                      onClick={() => handleToggleActive(agent)}
                      title={agent.is_active ? "Deactivate" : "Activate"}
                      className="text-slate-400 hover:text-white"
                    >
                      {agent.is_active ? (
                        <span className="flex items-center space-x-1 text-emerald-400 text-xs font-medium">
                          <CheckCircle className="w-4 h-4" />
                          <span>Active</span>
                        </span>
                      ) : (
                        <span className="flex items-center space-x-1 text-slate-500 text-xs font-medium">
                          <XCircle className="w-4 h-4" />
                          <span>Disabled</span>
                        </span>
                      )}
                    </button>
                  </div>
                </div>

                <p className="text-xs text-slate-300 mt-4 leading-relaxed line-clamp-2">
                  {agent.description}
                </p>

                {/* Manifesto Snippet */}
                <div className="mt-3 p-3 bg-navy-950/70 border border-navy-850 rounded-lg">
                  <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold block mb-1">
                    Interest Manifesto
                  </span>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {agent.interest_manifesto}
                  </p>
                </div>
              </div>

              {/* Footer info */}
              <div className="mt-4 pt-3 border-t border-navy-800 flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center space-x-3">
                  <span className="flex items-center space-x-1 text-[11px]">
                    <ShieldCheck className="w-3.5 h-3.5 text-accent-cyan" />
                    <span>Trust: {Math.round(agent.trust_score * 100)}%</span>
                  </span>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-navy-800 text-indigo-300">
                    Mode: {agent.response_mode}
                  </span>
                </div>
                <span className="text-[11px] text-slate-500 font-mono">
                  {agent.webhook_url.replace("http://", "").replace("https://", "").slice(0, 24)}...
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Registration Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-navy-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-navy-900 border border-navy-750 rounded-2xl w-full max-w-xl p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white tracking-tight">Register New AI Agent</h3>
            <p className="text-xs text-slate-400 mt-1">
              Provide corporate manifesto to automatically generate pgvector embeddings for semantic routing.
            </p>

            {errorMsg && (
              <div className="mt-3 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-xs text-rose-300">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleRegister} className="mt-4 space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Company Name</label>
                  <input
                    required
                    type="text"
                    placeholder="e.g. Swiggy"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Agent Name</label>
                  <input
                    required
                    type="text"
                    placeholder="e.g. Swiggy Growth Agent"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Industry Category</label>
                  <input
                    required
                    type="text"
                    placeholder="e.g. Food Delivery / Payments"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Response Mode</label>
                  <select
                    value={responseMode}
                    onChange={(e: any) => setResponseMode(e.target.value)}
                    className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                  >
                    <option value="auto">Autonomous (Auto-publish)</option>
                    <option value="human_approval">Human Approval Required</option>
                    <option value="ignore">Ignore Notifications</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Agent Description</label>
                <input
                  required
                  type="text"
                  placeholder="Operational role and scope"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Interest Manifesto (Used for Embedding Generation)</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Detail business objectives, promotional interests, partnership criteria, and target synergies..."
                  value={manifesto}
                  onChange={(e) => setManifesto(e.target.value)}
                  className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Webhook URL (Signed with HMAC-SHA256)</label>
                <input
                  required
                  type="text"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full bg-navy-950 border border-navy-750 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-cyan"
                />
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
                  {submitting ? "Embedding & Registering..." : "Register Agent"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* API Key Modal */}
      {apiKeyModal && (
        <div className="fixed inset-0 z-50 bg-navy-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-navy-900 border border-navy-750 rounded-2xl w-full max-w-md p-6 shadow-2xl text-center">
            <div className="w-12 h-12 rounded-xl bg-accent-cyan/15 text-accent-cyan mx-auto flex items-center justify-center mb-3">
              <Key className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight">Agent Registered!</h3>
            <p className="text-xs text-slate-400 mt-1">
              Save this API key for <strong className="text-white">{apiKeyModal.company}</strong>. It is hashed with SHA-256 and will never be shown again.
            </p>

            <div className="mt-4 p-3 bg-navy-950 border border-navy-800 rounded-lg font-mono text-xs text-accent-cyan break-all select-all">
              {apiKeyModal.key}
            </div>

            <button
              onClick={() => setApiKeyModal(null)}
              className="mt-5 w-full py-2.5 rounded-lg text-xs font-semibold bg-accent-cyan text-navy-950 hover:bg-cyan-400"
            >
              I Have Saved My API Key
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
