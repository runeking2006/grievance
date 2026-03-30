"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/hooks/useAuth";

export function LoginPage() {
  const { loginMutation, registerMutation } = useAuth();
  const [mode, setMode] = useState<"signin" | "register">("signin");
  const [signInForm, setSignInForm] = useState({ email: "", apiKey: "" });
  const [registerForm, setRegisterForm] = useState({ email: "", fullName: "" });

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#163855,transparent_34%),radial-gradient(circle_at_bottom_right,#59371f,transparent_26%),var(--bg)] px-4 py-10 text-[var(--text-strong)]">
      <div className="mx-auto grid min-h-[88vh] max-w-6xl gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="flex flex-col justify-between bg-[linear-gradient(160deg,rgba(242,107,91,0.18),transparent_48%),var(--panel-strong)] p-8 lg:p-10">
          <div>
            <p className="text-xs uppercase tracking-[0.34em] text-[var(--text-muted)]">Production Frontend</p>
            <h1 className="mt-6 max-w-xl text-5xl font-semibold leading-tight">
              AI grievance management with live triage, escalation, and operational analytics.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-[var(--text-soft)]">
              Sign in with an issued API key or register a new identity to access the user portal, admin dashboard, and system observability feeds.
            </p>
          </div>

          <div className="grid gap-4 pt-10 md:grid-cols-3">
            {[
              ["Semantic retrieval", "Real complaint similarity and generated insight"],
              ["SLA escalation", "Deadline-aware processing with escalation monitoring"],
              ["Live observability", "Health, metrics, queue status, and notifications"],
            ].map(([title, description]) => (
              <div key={title} className="rounded-3xl border border-white/10 bg-black/20 p-4">
                <p className="text-sm font-semibold">{title}</p>
                <p className="mt-2 text-sm text-[var(--text-soft)]">{description}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 lg:p-8">
          <div className="inline-flex rounded-full bg-black/20 p-1">
            <button
              type="button"
              onClick={() => setMode("signin")}
              className={`rounded-full px-4 py-2 text-sm font-medium ${mode === "signin" ? "bg-[var(--brand)] text-white" : "text-[var(--text-soft)]"}`}
            >
              Sign in
            </button>
            <button
              type="button"
              onClick={() => setMode("register")}
              className={`rounded-full px-4 py-2 text-sm font-medium ${mode === "register" ? "bg-[var(--brand)] text-white" : "text-[var(--text-soft)]"}`}
            >
              Register
            </button>
          </div>

          {mode === "signin" ? (
            <form
              className="mt-6 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                loginMutation.mutate(signInForm);
              }}
            >
              <Input
                placeholder="Email"
                type="email"
                value={signInForm.email}
                onChange={(event) => setSignInForm((current) => ({ ...current, email: event.target.value }))}
              />
              <Input
                placeholder="API key"
                value={signInForm.apiKey}
                onChange={(event) => setSignInForm((current) => ({ ...current, apiKey: event.target.value }))}
              />
              <Button type="submit" className="w-full" loading={loginMutation.isPending}>
                Access workspace
              </Button>
            </form>
          ) : (
            <form
              className="mt-6 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                registerMutation.mutate(registerForm);
              }}
            >
              <Input
                placeholder="Full name"
                value={registerForm.fullName}
                onChange={(event) => setRegisterForm((current) => ({ ...current, fullName: event.target.value }))}
              />
              <Input
                placeholder="Email"
                type="email"
                value={registerForm.email}
                onChange={(event) => setRegisterForm((current) => ({ ...current, email: event.target.value }))}
              />
              <Button type="submit" className="w-full" loading={registerMutation.isPending}>
                Create account
              </Button>
              <p className="text-sm text-[var(--text-soft)]">
                Registration returns an API key and immediately creates a JWT-backed session.
              </p>
            </form>
          )}

          <div className="mt-8 rounded-3xl border border-white/10 bg-black/15 p-4 text-sm text-[var(--text-soft)]">
            <p className="font-semibold text-[var(--text-strong)]">Testing tips</p>
            <ul className="mt-3 space-y-2">
              <li>Register once to receive an API key.</li>
              <li>Use sign in when you want to re-enter with an existing API key.</li>
              <li>Admin and staff roles unlock the full dashboard and analytics workspace.</li>
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
}
