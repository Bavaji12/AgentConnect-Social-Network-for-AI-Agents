import {
  Agent, Post, Comment, NotificationItem, RoutingLog,
  DashboardOverview, RoutingAnalytics, FeedbackAnalytics
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getHeaders(token?: string): HeadersInit {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  const authToken = token || (typeof window !== "undefined" ? localStorage.getItem("agentconnect_token") : null);
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return headers;
}

export const api = {
  // Auth
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Authentication failed");
    }
    return res.json();
  },

  async registerUser(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(err.detail || "Registration failed");
    }
    return res.json();
  },

  // Dashboard
  async getDashboardOverview(): Promise<DashboardOverview> {
    const res = await fetch(`${API_BASE}/dashboard/overview`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load dashboard overview");
    return res.json();
  },

  // Agents
  async getAgents(search?: string, isActive?: boolean): Promise<Agent[]> {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (isActive !== undefined) params.append("is_active", String(isActive));
    const res = await fetch(`${API_BASE}/agents?${params.toString()}`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load agents");
    return res.json();
  },

  async getAgent(id: string): Promise<Agent> {
    const res = await fetch(`${API_BASE}/agents/${id}`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load agent");
    return res.json();
  },

  async registerAgent(data: {
    company_name: string;
    agent_name: string;
    industry_category: string;
    description: string;
    interest_manifesto: string;
    webhook_url: string;
    response_mode: string;
  }) {
    const res = await fetch(`${API_BASE}/agents/register`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(err.detail || "Agent registration failed");
    }
    return res.json();
  },

  async updateAgent(id: string, updates: Partial<Agent>) {
    const res = await fetch(`${API_BASE}/agents/${id}`, {
      method: "PATCH",
      headers: getHeaders(),
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error("Failed to update agent");
    return res.json();
  },

  // Posts
  async getPosts(search?: string, category?: string): Promise<Post[]> {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (category) params.append("category", category);
    const res = await fetch(`${API_BASE}/posts?${params.toString()}`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load posts");
    return res.json();
  },

  async getPost(id: string) {
    const res = await fetch(`${API_BASE}/posts/${id}`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load post details");
    return res.json();
  },

  async createPost(data: {
    title: string;
    content: string;
    category: string;
    tags: string[];
    author_agent_id?: string;
  }) {
    const headers = getHeaders();
    if (data.author_agent_id) {
      (headers as Record<string, string>)["X-Author-Agent-Id"] = data.author_agent_id;
    }
    const res = await fetch(`${API_BASE}/posts`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        title: data.title,
        content: data.content,
        category: data.category,
        tags: data.tags
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Create post failed" }));
      throw new Error(err.detail || "Failed to create post");
    }
    return res.json();
  },

  // Comments
  async createComment(postId: string, content: string, authorAgentId?: string) {
    const headers = getHeaders();
    if (authorAgentId) {
      (headers as Record<string, string>)["X-Author-Agent-Id"] = authorAgentId;
    }
    const res = await fetch(`${API_BASE}/posts/${postId}/comments`, {
      method: "POST",
      headers,
      body: JSON.stringify({ content, generated_by_llm: false }),
    });
    if (!res.ok) throw new Error("Failed to post comment");
    return res.json();
  },

  async updateCommentApproval(commentId: string, status: "approved" | "rejected") {
    const res = await fetch(`${API_BASE}/comments/${commentId}/approval`, {
      method: "PATCH",
      headers: getHeaders(),
      body: JSON.stringify({ approval_status: status }),
    });
    if (!res.ok) throw new Error("Failed to update comment approval");
    return res.json();
  },

  // Routing
  async runRoutingForPost(postId: string, threshold?: number) {
    const url = threshold !== undefined
      ? `${API_BASE}/routing/${postId}/run?threshold=${threshold}`
      : `${API_BASE}/routing/${postId}/run`;
    const res = await fetch(url, {
      method: "POST",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to execute routing");
    return res.json();
  },

  async getRoutingResults(postId: string): Promise<RoutingLog[]> {
    const res = await fetch(`${API_BASE}/routing/${postId}/results`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load routing results");
    return res.json();
  },

  async getRoutingAnalytics(): Promise<RoutingAnalytics> {
    const res = await fetch(`${API_BASE}/routing/analytics`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load routing analytics");
    return res.json();
  },

  // Notifications
  async getNotifications(status?: string): Promise<NotificationItem[]> {
    const url = status ? `${API_BASE}/notifications?status=${status}` : `${API_BASE}/notifications`;
    const res = await fetch(url, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load notifications");
    return res.json();
  },

  async retryNotification(id: string) {
    const res = await fetch(`${API_BASE}/notifications/${id}/retry`, {
      method: "POST",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to retry notification");
    return res.json();
  },

  // Feedback
  async getFeedbackAnalytics(): Promise<FeedbackAnalytics> {
    const res = await fetch(`${API_BASE}/feedback/analytics`, {
      headers: getHeaders(),
      cache: "no-store"
    });
    if (!res.ok) throw new Error("Failed to load feedback analytics");
    return res.json();
  }
};
