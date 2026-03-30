import type { ReactNode } from "react";

export function Card({
  title,
  eyebrow,
  action,
  children,
  className = "",
}: {
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-[28px] border border-white/10 bg-[var(--panel)] p-5 shadow-[0_22px_80px_rgba(0,0,0,0.18)] ${className}`}>
      {title || eyebrow || action ? (
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            {eyebrow ? <p className="text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]">{eyebrow}</p> : null}
            {title ? <h3 className="mt-1 text-lg font-semibold text-[var(--text-strong)]">{title}</h3> : null}
          </div>
          {action}
        </div>
      ) : null}
      {children}
    </section>
  );
}
