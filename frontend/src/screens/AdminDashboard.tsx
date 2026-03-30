"use client";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { useDashboard } from "@/hooks/useDashboard";
import { formatDateTime, getQueueLoad } from "@/utils/helpers";

export function AdminDashboardPage() {
  const { stats, highPriority, repeated, bottleneck, areaInsights, health, metrics } = useDashboard();

  const queueLoad = getQueueLoad(metrics.data?.counters ?? {}, metrics.data?.gauges ?? {});
  const dbConnected = health.data?.status === "ok";

  return (
    <div className="space-y-6">
      <div className="grid gap-4 xl:grid-cols-5">
        {stats.isLoading ? (
          Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-32 w-full" />)
        ) : (
          <>
            <StatCard label="Total complaints" value={stats.data?.total ?? 0} />
            <StatCard label="High priority" value={stats.data?.high_priority ?? 0} />
            <StatCard label="Repeated issues" value={stats.data?.repeated ?? 0} />
            <StatCard label="Bottleneck load" value={stats.data?.bottleneck_count ?? 0} />
            <StatCard label="Worker health" value={health.data?.worker_running ? "Live" : "Offline"} />
          </>
        )}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card eyebrow="Priority Desk" title="High priority alerts">
          <div className="space-y-3">
            {highPriority.data?.map((item) => (
              <div key={`${item.complaint_text}-${item.created_at}`} className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="text-sm font-medium text-[var(--text-strong)]">{item.complaint_text}</p>
                  <Badge tone={item.status === "Escalated" ? "danger" : "warning"}>{item.status}</Badge>
                </div>
                <p className="mt-3 text-sm text-[var(--text-soft)]">
                  Department: {item.department ?? "Unknown"} | Deadline: {formatDateTime(item.deadline)}
                </p>
              </div>
            ))}
            {highPriority.data?.length === 0 ? <p className="text-sm text-[var(--text-soft)]">No active high-priority complaints.</p> : null}
          </div>
        </Card>

        <Card eyebrow="System Health" title="Operational checks">
          <div className="space-y-4">
            <HealthRow label="API" value={health.data?.status === "ok" ? "Healthy" : "Unknown"} tone={health.data?.status === "ok" ? "success" : "warning"} />
            <HealthRow
              label="Worker"
              value={health.data?.worker_running ? "Running" : "Offline"}
              tone={health.data?.worker_running ? "success" : "danger"}
            />
            <HealthRow label="Queue Load" value={queueLoad} tone={queueLoad === "High" ? "danger" : queueLoad === "Medium" ? "warning" : "success"} />
            <HealthRow label="DB" value={dbConnected ? "Connected" : "Unknown"} tone={dbConnected ? "success" : "warning"} />

            <div className="rounded-3xl border border-white/10 bg-black/15 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">Bottleneck</p>
              <p className="mt-3 text-lg font-semibold">{bottleneck.data?.bottleneck ?? "No data"}</p>
              <p className="mt-2 text-sm text-[var(--text-soft)]">{bottleneck.data?.reason ?? "Awaiting complaint load"}</p>
            </div>

            <div className="rounded-3xl border border-white/10 bg-black/15 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">Area impact</p>
              <p className="mt-3 text-lg font-semibold">{areaInsights.data?.length ?? 0} active clusters</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card eyebrow="Repeated patterns" title="Recurring complaint texts">
          <div className="space-y-3">
            {repeated.data?.map((item) => (
              <div key={item.complaint_text} className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <p className="text-sm font-medium text-[var(--text-strong)]">{item.complaint_text}</p>
                <p className="mt-2 text-sm text-[var(--text-soft)]">Seen {item.count} times</p>
              </div>
            ))}
          </div>
        </Card>

        <Card eyebrow="Area recommendations" title="Multiple-user issue clusters">
          <div className="space-y-3">
            {areaInsights.data?.map((item) => (
              <div key={`${item.location}-${item.issue}`} className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="text-sm font-medium text-[var(--text-strong)]">
                    {item.location} | {item.issue}
                  </p>
                  <Badge tone="warning">{item.count} reports</Badge>
                </div>
                <p className="mt-2 text-sm text-[var(--text-soft)]">{item.insight}</p>
              </div>
            ))}
            {areaInsights.data?.length === 0 ? <p className="text-sm text-[var(--text-soft)]">No area-level cluster detected.</p> : null}
          </div>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card className="min-h-32">
      <p className="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{label}</p>
      <p className="mt-6 text-4xl font-semibold text-[var(--text-strong)]">{value}</p>
    </Card>
  );
}

function HealthRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "success" | "warning" | "danger";
}) {
  return (
    <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-black/15 p-4">
      <p className="text-sm text-[var(--text-soft)]">{label}</p>
      <Badge tone={tone}>{value}</Badge>
    </div>
  );
}
