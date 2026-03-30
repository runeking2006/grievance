"use client";

import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input, Textarea } from "@/components/ui/Input";
import { Skeleton } from "@/components/ui/Skeleton";
import { useComplaint, useJobStatus, useMyComplaints } from "@/hooks/useComplaint";
import { clamp, extractKeywords, formatDateTime, getConfidenceTone } from "@/utils/helpers";

const PIPELINE_STAGES = [
  { key: "classification", label: "Classification done" },
  { key: "priority", label: "Priority assigned" },
  { key: "similarity", label: "Similarity search completed" },
  { key: "routing", label: "Routing assigned" },
] as const;

export function UserDashboardPage() {
  const { complaintMutation, asyncComplaintMutation } = useComplaint();
  const [form, setForm] = useState({ text: "", location: "" });
  const [mode, setMode] = useState<"sync" | "async">("sync");
  const [activeJobId, setActiveJobId] = useState<number | null>(null);
  const [lastSubmittedText, setLastSubmittedText] = useState("");
  const [stageTick, setStageTick] = useState<number>(0);

  const myComplaintsQuery = useMyComplaints();
  const jobQuery = useJobStatus(activeJobId);

  const latestResponse = complaintMutation.data;
  const activeJob = jobQuery.data;
  const busy = complaintMutation.isPending || asyncComplaintMutation.isPending;

  useEffect(() => {
    if (!complaintMutation.isPending) {
      return;
    }

    const interval = window.setInterval(() => {
      setStageTick((current) => current + 1);
    }, 650);

    return () => window.clearInterval(interval);
  }, [complaintMutation.isPending]);

  const stageIndex = latestResponse
    ? PIPELINE_STAGES.length - 1
    : complaintMutation.isPending
      ? Math.min(stageTick, PIPELINE_STAGES.length - 1)
      : -1;

  const confidence = useMemo(() => {
    if (!latestResponse) {
      return 0;
    }
    const keywordBoost = extractKeywords(lastSubmittedText).length * 4;
    const similarityBoost = latestResponse.similar_complaints.length * 6;
    const urgencyBoost = latestResponse.urgency.toLowerCase() === "high" ? 8 : latestResponse.urgency.toLowerCase() === "medium" ? 4 : 0;
    return clamp(58 + keywordBoost + similarityBoost + urgencyBoost, 32, 97);
  }, [lastSubmittedText, latestResponse]);

  const confidenceTone = getConfidenceTone(confidence);
  const extractedKeywords = useMemo(() => extractKeywords(lastSubmittedText), [lastSubmittedText]);
  const similarMatches = latestResponse?.similar_complaints.length ?? 0;

  return (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <div className="space-y-6">
        <Card eyebrow="User Portal" title="Submit a grievance">
          <div className="mb-4 inline-flex rounded-full bg-black/20 p-1">
            <button
              type="button"
              onClick={() => setMode("sync")}
              className={`rounded-full px-4 py-2 text-sm font-medium ${mode === "sync" ? "bg-[var(--brand)] text-white" : "text-[var(--text-soft)]"}`}
            >
              Sync response
            </button>
            <button
              type="button"
              onClick={() => setMode("async")}
              className={`rounded-full px-4 py-2 text-sm font-medium ${mode === "async" ? "bg-[var(--brand)] text-white" : "text-[var(--text-soft)]"}`}
            >
              Async job
            </button>
          </div>

          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              setLastSubmittedText(form.text);
              setStageTick(0);
              if (mode === "sync") {
                complaintMutation.mutate(
                  { text: form.text, location: form.location || undefined },
                  {
                    onSuccess: () => setForm({ text: "", location: form.location }),
                  },
                );
              } else {
                asyncComplaintMutation.mutate(
                  { text: form.text, location: form.location || undefined },
                  {
                    onSuccess: (job) => {
                      setActiveJobId(job.job_id);
                      setForm({ text: "", location: form.location });
                    },
                  },
                );
              }
            }}
          >
            <Textarea
              placeholder="Describe the grievance in detail."
              value={form.text}
              onChange={(event) => setForm((current) => ({ ...current, text: event.target.value }))}
            />
            <Input
              placeholder="Location / district / block"
              value={form.location}
              onChange={(event) => setForm((current) => ({ ...current, location: event.target.value }))}
            />
            <Button type="submit" loading={busy} className="w-full" disabled={!form.text.trim()}>
              {mode === "sync" ? "Run AI triage" : "Queue complaint"}
            </Button>
          </form>
        </Card>

        <Card eyebrow="Pipeline" title="Real-time processing stages">
          <div className="space-y-3">
            {PIPELINE_STAGES.map((stage, index) => {
              const completed = latestResponse ? true : index <= stageIndex;
              const active = complaintMutation.isPending && index === stageIndex;
              return (
                <div key={stage.key} className="flex items-center justify-between rounded-3xl border border-white/10 bg-black/15 px-4 py-3">
                  <p className="text-sm text-[var(--text-soft)]">{stage.label}</p>
                  {completed ? (
                    <Badge tone="success">Done</Badge>
                  ) : active ? (
                    <Badge tone="warning">Running</Badge>
                  ) : (
                    <Badge tone="neutral">Waiting</Badge>
                  )}
                </div>
              );
            })}
          </div>
          <p className="mt-4 text-sm text-[var(--text-soft)]">
            {complaintMutation.isPending
              ? "The backend pipeline is processing classification, priority, similarity retrieval, and routing."
              : "Each stage becomes visible here as the backend completes AI triage."}
          </p>
        </Card>

        <Card eyebrow="Queue" title="Async processing status">
          {activeJob ? (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Badge tone={activeJob.status === "completed" ? "success" : activeJob.status === "failed" ? "danger" : "warning"}>
                  {activeJob.status}
                </Badge>
                <p className="text-sm text-[var(--text-soft)]">Job #{activeJob.job_id}</p>
                <Badge tone={jobQuery.isLive ? "success" : "neutral"}>{jobQuery.isLive ? "Live socket" : "Polling fallback"}</Badge>
              </div>
              <p className="text-sm text-[var(--text-soft)]">
                Background enrichment uses the backend worker or Celery depending on deployment settings.
              </p>
              {activeJob.error_message ? <p className="text-sm text-rose-300">{activeJob.error_message}</p> : null}
            </div>
          ) : jobQuery.isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : (
            <p className="text-sm text-[var(--text-soft)]">No active async job. Queue a complaint to watch progress here.</p>
          )}
        </Card>
      </div>

      <div className="space-y-6">
        <Card eyebrow="AI Result" title="Latest triage">
          {latestResponse ? (
            <div className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <Metric label="Category" value={latestResponse.category} />
                <Metric label="Priority" value={latestResponse.urgency} />
                <Metric label="Department" value={latestResponse.department} />
                <Metric label="Confidence" value={`${confidence}%`} />
              </div>

              <div className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">Confidence visualization</p>
                  <Badge tone={confidenceTone}>{confidence >= 80 ? "High" : confidence >= 50 ? "Medium" : "Low"} confidence</Badge>
                </div>
                <div className="mt-4 h-3 overflow-hidden rounded-full bg-white/10">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      confidenceTone === "success"
                        ? "bg-emerald-400"
                        : confidenceTone === "warning"
                          ? "bg-amber-400"
                          : "bg-rose-400"
                    }`}
                    style={{ width: `${confidence}%` }}
                  />
                </div>
                <p className="mt-3 text-sm text-[var(--text-soft)]">Explainability score based on extracted keywords, urgency strength, and semantic matches.</p>
              </div>

              <div className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">Insight</p>
                <p className="mt-3 text-sm leading-6 text-[var(--text-soft)]">{latestResponse.insight}</p>
              </div>

              <div className="rounded-3xl border border-white/10 bg-black/15 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">Why this result</p>
                <div className="mt-4 space-y-3 text-sm text-[var(--text-soft)]">
                  <p>Keywords detected: {extractedKeywords.length > 0 ? extractedKeywords.map((word) => `"${word}"`).join(", ") : "No strong keywords extracted"}</p>
                  <p>Similar complaints: {similarMatches} semantic matches retrieved from prior grievance history.</p>
                  <p>Department mapping rule triggered: {latestResponse.category} → {latestResponse.department}.</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Badge tone={latestResponse.escalated ? "danger" : "warning"}>{latestResponse.status}</Badge>
                <Badge tone="neutral">Escalation level {latestResponse.escalation_level}</Badge>
                <Badge tone="neutral">Deadline {formatDateTime(latestResponse.deadline)}</Badge>
              </div>

              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">Similar cases</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {latestResponse.similar_complaints.length > 0 ? (
                    latestResponse.similar_complaints.map((item) => (
                      <span key={item} className="rounded-full bg-white/10 px-3 py-2 text-sm text-[var(--text-soft)]">
                        {item}
                      </span>
                    ))
                  ) : (
                    <span className="rounded-full bg-white/6 px-3 py-2 text-sm text-[var(--text-muted)]">No related cases retrieved yet</span>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-soft)]">Submit a complaint to see category, urgency, insight, and similar-case retrieval.</p>
          )}
        </Card>

        <Card eyebrow="History" title="My complaints">
          {myComplaintsQuery.isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
            </div>
          ) : (
            <div className="space-y-3">
              {myComplaintsQuery.data?.map((complaint) => (
                <div key={complaint.complaint_id} className="rounded-3xl border border-white/10 bg-black/15 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-[var(--text-strong)]">{complaint.complaint_text}</p>
                      <p className="mt-2 text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{formatDateTime(complaint.created_at)}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Badge tone={complaint.escalated ? "danger" : "neutral"}>{complaint.status}</Badge>
                      <Badge tone="neutral">{complaint.category ?? "Pending category"}</Badge>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-[var(--text-soft)]">
                    Department: {complaint.department ?? "Awaiting routing"} | Priority: {complaint.urgency ?? "Awaiting triage"} | Processing:{" "}
                    {complaint.processing_status}
                  </p>
                </div>
              ))}
              {myComplaintsQuery.data?.length === 0 ? <p className="text-sm text-[var(--text-soft)]">No complaints submitted yet.</p> : null}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-black/15 p-4">
      <p className="text-xs uppercase tracking-[0.22em] text-[var(--text-muted)]">{label}</p>
      <p className="mt-3 text-lg font-semibold text-[var(--text-strong)]">{value}</p>
    </div>
  );
}
