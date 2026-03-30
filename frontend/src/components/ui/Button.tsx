import type { ButtonHTMLAttributes, ReactNode } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  tone?: "primary" | "secondary" | "ghost" | "danger";
  loading?: boolean;
  children: ReactNode;
};

const toneClasses: Record<NonNullable<Props["tone"]>, string> = {
  primary: "bg-[var(--brand)] text-white hover:bg-[var(--brand-strong)]",
  secondary: "bg-white/10 text-[var(--text-strong)] ring-1 ring-white/15 hover:bg-white/15",
  ghost: "bg-transparent text-[var(--text-soft)] hover:bg-white/8",
  danger: "bg-[var(--danger)] text-white hover:bg-[#cf3d4e]",
};

export function Button({ tone = "primary", loading, children, className = "", ...props }: Props) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${toneClasses[tone]} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent" /> : null}
      {children}
    </button>
  );
}
