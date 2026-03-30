import { apiClient } from "@/api/client";

export type DashboardStats = {
  total: number;
  categories: Record<string, number>;
  high_priority: number;
  repeated: number;
  bottleneck?: string | null;
  bottleneck_count: number;
};

export type HighPriorityComplaint = {
  complaint_text: string;
  department?: string | null;
  status: string;
  deadline?: string | null;
  created_at: string;
};

export type RepeatedComplaint = {
  complaint_text: string;
  count: number;
};

export type Bottleneck = {
  bottleneck: string;
  reason: string;
  complaints: number;
};

export type AreaInsight = {
  location: string;
  issue: string;
  count: number;
  insight: string;
};

export type HealthStatus = {
  status: string;
  worker_running: boolean;
  app_started: boolean;
};

export type MetricsSnapshot = {
  counters: Record<string, number>;
  timers: Record<string, { count: number; avg_ms: number; max_ms: number }>;
  gauges: Record<string, number>;
};

export async function fetchStats(): Promise<DashboardStats> {
  const { data } = await apiClient.get<DashboardStats>("/stats");
  return data;
}

export async function fetchHighPriority(): Promise<HighPriorityComplaint[]> {
  const { data } = await apiClient.get<HighPriorityComplaint[]>("/high-priority");
  return data;
}

export async function fetchRepeated(): Promise<RepeatedComplaint[]> {
  const { data } = await apiClient.get<RepeatedComplaint[]>("/repeated");
  return data;
}

export async function fetchBottleneck(): Promise<Bottleneck> {
  const { data } = await apiClient.get<Bottleneck>("/bottleneck");
  return data;
}

export async function fetchAreaInsights(): Promise<AreaInsight[]> {
  const { data } = await apiClient.get<AreaInsight[]>("/area-insights");
  return data;
}

export async function fetchHealth(): Promise<HealthStatus> {
  const { data } = await apiClient.get<HealthStatus>("/health");
  return data;
}

export async function fetchMetrics(): Promise<MetricsSnapshot> {
  const { data } = await apiClient.get<MetricsSnapshot>("/metrics");
  return data;
}
