"use client";

import { useMemo, useState } from "react";

import { AreaInsightsChart } from "@/components/charts/AreaInsightsChart";
import { CategoryBarChart } from "@/components/charts/CategoryBarChart";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useDashboard } from "@/hooks/useDashboard";
import { getQueueLoad, percentage } from "@/utils/helpers";

export function AnalyticsPage() {
  const { stats, areaInsights, metrics, health } = useDashboard();
  const [districtFilter, setDistrictFilter] = useState("");

  const filteredAreas = useMemo(() => {
    const rows = areaInsights.data ?? [];
    if (!districtFilter.trim()) {
      return rows;
    }
    return rows.filter((item) => item.location.toLowerCase().includes(districtFilter.toLowerCase()));
  }, [areaInsights.data, districtFilter]);

  const categoryData = stats.data?.categories ?? {};
  const areaChartData = filteredAreas.map((item) => ({ location: item.location, count: item.count }));
  const queueLoad = getQueueLoad(metrics.data?.counters ?? {}, metrics.data?.gauges ?? {});
  const dominantCategory = Object.entries(categoryData).sort((left, right) => right[1] - left[1])[0];
  const totalClusterReports = filteredAreas.reduce((sum, item) => sum + item.count, 0);

  return (
    <div className="space-y-6">
      <Card eyebrow="Filters" title="Analytics controls">
        <div className="grid gap-4 md:grid-cols-[1fr_auto]">
          <Input
            placeholder="Filter by district / area / block"
            value={districtFilter}
            onChange={(event) => setDistrictFilter(event.target.value)}
          />
          <div className="rounded-3xl border border-white/10 bg-black/15 px-4 py-3 text-sm text-[var(--text-soft)]">
            Showing {filteredAreas.length} area insight rows
          </div>
        </div>
      </Card>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card eyebrow="Categories" title="Complaint distribution">
          <CategoryBarChart categories={categoryData} />
        </Card>

        <Card eyebrow="Locations" title="High-impact areas">
          <AreaInsightsChart data={areaChartData} />
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        <MetricCard label="Dominant category" value={dominantCategory?.[0] ?? "No data"} />
        <MetricCard label="Category share" value={dominantCategory && stats.data ? `${percentage(dominantCategory[1], stats.data.total)}%` : "0%"} />
        <MetricCard label="Cluster volume" value={`${totalClusterReports}`} />
        <MetricCard label="Operational queue" value={queueLoad} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card eyebrow="Area insights" title="Filtered impact table">
          <div className="space-y-3">
            {filteredAreas.map((item) => (
              <div key={`${item.location}-${item.issue}`} className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <p className="text-sm font-medium text-[var(--text-strong)]">
                  {item.location} | {item.issue}
                </p>
                <p className="mt-2 text-sm text-[var(--text-soft)]">
                  {item.count} complaints | {item.insight}
                </p>
              </div>
            ))}
            {filteredAreas.length === 0 ? <p className="text-sm text-[var(--text-soft)]">No matching area insights.</p> : null}
          </div>
        </Card>

        <Card eyebrow="Observability" title="Runtime metrics">
          <div className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <MetricCard label="API status" value={health.data?.status === "ok" ? "Healthy" : "Unknown"} />
              <MetricCard label="Queue load" value={queueLoad} />
              <MetricCard label="Worker" value={health.data?.worker_running ? "Running" : "Offline"} />
              <MetricCard label="High priority share" value={stats.data ? `${percentage(stats.data.high_priority, stats.data.total)}%` : "0%"} />
            </div>
            {Object.entries(metrics.data?.counters ?? {}).map(([key, value]) => (
              <div key={key} className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{key}</p>
                <p className="mt-3 text-2xl font-semibold">{value}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card eyebrow="Viva Flow" title="End-to-end system workflow">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          {[
            "Input Layer: user submits grievance text and location.",
            "AI Processing: classification, urgency, and embeddings are generated.",
            "RAG Engine: similar complaints are retrieved to detect patterns.",
            "Routing + SLA: department and deadline are assigned automatically.",
            "Storage + Dashboard: Neon stores the record and analytics update live.",
          ].map((step) => (
            <div key={step} className="rounded-3xl border border-white/10 bg-black/15 p-4 text-sm text-[var(--text-soft)]">
              {step}
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-[var(--text-soft)]">
          The system transforms unstructured complaints into actionable insights automatically.
        </p>
      </Card>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-black/15 p-4">
      <p className="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{label}</p>
      <p className="mt-3 text-xl font-semibold text-[var(--text-strong)]">{value}</p>
    </div>
  );
}
