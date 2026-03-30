import type { ReactNode } from "react";

import { APP_NAME } from "@/utils/constants";

type NavItem = {
  key: string;
  label: string;
};

export function AppShell({
  activePage,
  onNavigate,
  navItems,
  header,
  children,
}: {
  activePage: string;
  onNavigate: (page: string) => void;
  navItems: NavItem[];
  header: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#163855,transparent_34%),radial-gradient(circle_at_top_right,#493421,transparent_28%),var(--bg)] text-[var(--text-strong)]">
      <div className="mx-auto flex min-h-screen max-w-[1560px] gap-6 px-4 py-4 lg:px-6">
        <aside className="hidden w-72 shrink-0 rounded-[32px] border border-white/10 bg-[var(--panel-strong)] p-5 lg:flex lg:flex-col">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">AI Operations</p>
            <h1 className="mt-3 text-2xl font-semibold">{APP_NAME}</h1>
            <p className="mt-3 text-sm leading-6 text-[var(--text-soft)]">
              Live grievance triage, escalation, analytics, and observability in a single cockpit.
            </p>
          </div>

          <nav className="mt-10 space-y-2">
            {navItems.map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => onNavigate(item.key)}
                className={`flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm transition ${
                  activePage === item.key
                    ? "bg-[var(--brand)] text-white shadow-lg"
                    : "text-[var(--text-soft)] hover:bg-white/8 hover:text-[var(--text-strong)]"
                }`}
              >
                <span>{item.label}</span>
                <span className="text-xs uppercase tracking-[0.24em] opacity-70">open</span>
              </button>
            ))}
          </nav>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col gap-6">
          <header className="rounded-[28px] border border-white/10 bg-[var(--panel)] p-5 shadow-[0_20px_80px_rgba(0,0,0,0.15)]">
            {header}
          </header>
          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </div>
    </div>
  );
}
