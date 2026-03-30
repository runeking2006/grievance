export function formatDateTime(value?: string | null): string {
  if (!value) {
    return "Not available";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export function percentage(value: number, total: number): number {
  if (!total) {
    return 0;
  }
  return Math.round((value / total) * 100);
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function getConfidenceTone(value: number): "success" | "warning" | "danger" {
  if (value >= 80) {
    return "success";
  }
  if (value >= 50) {
    return "warning";
  }
  return "danger";
}

export function extractKeywords(text: string, limit = 4): string[] {
  const stopWords = new Set([
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "have",
    "from",
    "hostel",
    "block",
    "urgent",
    "issue",
    "complaint",
    "there",
    "been",
    "about",
    "into",
    "your",
    "their",
    "while",
  ]);

  return Array.from(
    new Set(
      text
        .toLowerCase()
        .match(/[a-z]{3,}/g)
        ?.filter((word) => !stopWords.has(word)) ?? [],
    ),
  ).slice(0, limit);
}

export function getQueueLoad(counters: Record<string, number>, gauges: Record<string, number>): "Low" | "Medium" | "High" {
  const pending =
    (gauges["queue.pending"] ?? 0) ||
    Math.max((counters["jobs.enqueued"] ?? 0) - (counters["jobs.completed"] ?? 0) - (counters["jobs.failed"] ?? 0), 0);

  if (pending >= 8) {
    return "High";
  }
  if (pending >= 3) {
    return "Medium";
  }
  return "Low";
}
