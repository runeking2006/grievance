"use client";

import { useEffect } from "react";

import { useUiStore } from "@/store/uiStore";

export function ToastViewport() {
  const toasts = useUiStore((state) => state.toasts);
  const removeToast = useUiStore((state) => state.removeToast);

  useEffect(() => {
    const timers = toasts.map((toast) => window.setTimeout(() => removeToast(toast.id), 3500));
    return () => timers.forEach((timer) => window.clearTimeout(timer));
  }, [toasts, removeToast]);

  return (
    <div className="pointer-events-none fixed right-6 top-6 z-50 flex w-full max-w-sm flex-col gap-3">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto rounded-3xl border px-4 py-3 shadow-2xl backdrop-blur ${
            toast.tone === "error"
              ? "border-rose-500/40 bg-rose-500/15"
              : toast.tone === "success"
                ? "border-emerald-500/40 bg-emerald-500/15"
                : "border-white/10 bg-[var(--panel)]"
          }`}
        >
          <p className="text-sm font-semibold text-[var(--text-strong)]">{toast.title}</p>
          {toast.description ? <p className="mt-1 text-sm text-[var(--text-soft)]">{toast.description}</p> : null}
        </div>
      ))}
    </div>
  );
}
