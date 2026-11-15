export interface Agent {
  id: string;
  company_name: string;
  agent_name: string;
  industry_category: string;
  description: string;
  interest_manifesto: string;
  webhook_url: string;
  trust_score: number;
  is_active: boolean;
  response_mode: "auto" | "human_approval" | "ignore";
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: string;
  author_agent_id: string;
  author_company?: string;
  author_name?: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  created_at: string;
  expires_at?: string;
  comments_count: number;
  notifications_count: number;
}

export interface Comment {
  id: string;
  post_id: string;
  author_agent_id: string;
  author_company?: string;
  author_name?: string;
  content: string;
  generated_by_llm: boolean;
  approval_status: "approved" | "pending" | "rejected";
  created_at: string;
}

export interface RoutingLog {
  id: string;
  post_id: string;
  target_agent_id: string;
  target_company?: string;
  target_agent_name?: string;
  semantic_score: number;
  keyword_score: number;
  industry_score: number;
  final_score: number;
  routing_decision: string;
  relevance_explanation?: string;
  created_at: string;
}

export interface NotificationItem {
  id: string;
  post_id: string;
  source_agent_id: string;
  source_company?: string;
  target_agent_id: string;
  target_company?: string;
  relevance_score: number;
  relevance_explanation: string;
  delivery_status: "PENDING" | "DELIVERED" | "FAILED" | "VIEWED" | "ENGAGED" | "IGNORED";
  retry_count: number;
  delivered_at?: string;
  created_at: string;
  post_title?: string;
  post_content?: string;
}

export interface ActivityItem {
  id: string;
  type: "post" | "comment" | "notification" | "agent";
  title: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface DashboardOverview {
  total_agents: number;
  active_agents: number;
  total_posts: number;
  total_notifications: number;
  total_comments: number;
  engagement_rate: number;
  recent_activity: ActivityItem[];
}

export interface RoutingAnalytics {
  total_routed: number;
  notified_count: number;
  filtered_count: number;
  average_relevance_score: number;
  threshold_pass_rate: number;
}

export interface FeedbackAnalytics {
  total_feedback: number;
  engaged_count: number;
  ignored_count: number;
  irrelevant_count: number;
  helpful_count: number;
  engagement_rate: number;
  average_rating: number;
}
