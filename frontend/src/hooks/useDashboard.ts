"use client";

import { useQueries } from "@tanstack/react-query";

import {
  fetchAreaInsights,
  fetchBottleneck,
  fetchHealth,
  fetchHighPriority,
  fetchMetrics,
  fetchRepeated,
  fetchStats,
} from "@/api/dashboard";
import { QUERY_KEYS } from "@/utils/constants";

export function useDashboard() {
  const [stats, highPriority, repeated, bottleneck, areaInsights, health, metrics] = useQueries({
    queries: [
      { queryKey: QUERY_KEYS.stats, queryFn: fetchStats },
      { queryKey: QUERY_KEYS.highPriority, queryFn: fetchHighPriority },
      { queryKey: QUERY_KEYS.repeated, queryFn: fetchRepeated },
      { queryKey: QUERY_KEYS.bottleneck, queryFn: fetchBottleneck },
      { queryKey: QUERY_KEYS.areaInsights, queryFn: fetchAreaInsights },
      { queryKey: QUERY_KEYS.health, queryFn: fetchHealth, refetchInterval: 20000 },
      { queryKey: QUERY_KEYS.metrics, queryFn: fetchMetrics, refetchInterval: 20000 },
    ],
  });

  return { stats, highPriority, repeated, bottleneck, areaInsights, health, metrics };
}
