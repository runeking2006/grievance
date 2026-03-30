export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

export const WS_BASE_URL = API_BASE_URL.replace(/^http/i, "ws");

export const APP_NAME = "Grievance Command Center";

export const QUERY_KEYS = {
  me: ["me"] as const,
  myComplaints: ["my-complaints"] as const,
  stats: ["stats"] as const,
  highPriority: ["high-priority"] as const,
  repeated: ["repeated"] as const,
  bottleneck: ["bottleneck"] as const,
  areaInsights: ["area-insights"] as const,
  health: ["health"] as const,
  metrics: ["metrics"] as const,
  job: (jobId: number | null) => ["job", jobId] as const,
};

export const APP_PAGES = [
  { key: "user", label: "User Portal" },
  { key: "admin", label: "Admin Dashboard" },
  { key: "analytics", label: "Analytics" },
] as const;

export const ADMIN_ROLES = new Set(["admin", "staff"]);
