"use client";

import dynamic from "next/dynamic";
import { useMemo, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { ToastViewport } from "@/components/ui/ToastViewport";
import { useAuth } from "@/hooks/useAuth";
import type { AuthUser } from "@/store/authStore";
import { useAuthStore } from "@/store/authStore";
import { ADMIN_ROLES, APP_PAGES } from "@/utils/constants";

const LoginPage = dynamic(() => import("@/screens/Login").then((module) => module.LoginPage), {
  loading: () => <div className="min-h-screen bg-[var(--bg)]" />,
});
const UserDashboardPage = dynamic(() => import("@/screens/UserDashboard").then((module) => module.UserDashboardPage), {
  loading: () => <Skeleton className="h-[70vh] w-full" />,
});
const AdminDashboardPage = dynamic(() => import("@/screens/AdminDashboard").then((module) => module.AdminDashboardPage), {
  loading: () => <Skeleton className="h-[70vh] w-full" />,
});
const AnalyticsPage = dynamic(() => import("@/screens/Analytics").then((module) => module.AnalyticsPage), {
  loading: () => <Skeleton className="h-[70vh] w-full" />,
});

export default function App() {
  const { hydrated, isAuthenticated, currentUser, meQuery, signOut } = useAuth();
  const persistedUser = useAuthStore((state) => state.user);
  const user: AuthUser | null = currentUser ?? persistedUser;
  const isAdmin = user ? ADMIN_ROLES.has(user.role) : false;
  const navItems = useMemo(() => APP_PAGES.filter((item) => item.key === "user" || isAdmin), [isAdmin]);
  const [activePage, setActivePage] = useState<string>("user");

  if (!hydrated) {
    return <div className="min-h-screen bg-[var(--bg)]" />;
  }

  if (!isAuthenticated) {
    return (
      <>
        <ToastViewport />
        <LoginPage />
      </>
    );
  }

  const page =
    activePage === "admin" && isAdmin ? (
      <AdminDashboardPage />
    ) : activePage === "analytics" && isAdmin ? (
      <AnalyticsPage />
    ) : (
      <UserDashboardPage />
    );

  return (
    <>
      <ToastViewport />
      <AppShell
        activePage={activePage}
        onNavigate={setActivePage}
        navItems={navItems}
        header={
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Live backend integration</p>
              <h2 className="mt-2 text-3xl font-semibold text-[var(--text-strong)]">
                {activePage === "user" ? "User operations" : activePage === "admin" ? "Admin command view" : "Analytics studio"}
              </h2>
              <p className="mt-2 text-sm text-[var(--text-soft)]">
                Signed in as {user?.email ?? "Unknown"} | role {user?.role ?? "unknown"} |{" "}
                {meQuery.isFetching ? "Refreshing identity" : "Session active"}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="rounded-full border border-white/10 bg-black/20 px-4 py-2 text-sm text-[var(--text-soft)]">JWT active</div>
              <Button tone="secondary" onClick={signOut}>
                Sign out
              </Button>
            </div>
          </div>
        }
      >
        {page}
      </AppShell>
    </>
  );
}
