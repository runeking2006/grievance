"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

export type AuthUser = {
  id: string;
  email: string;
  full_name?: string | null;
  role: string;
};

type AuthState = {
  token: string | null;
  apiKey: string | null;
  user: AuthUser | null;
  hydrated: boolean;
  setHydrated: (value: boolean) => void;
  setSession: (payload: { token: string; apiKey?: string | null; user: AuthUser }) => void;
  updateUser: (user: AuthUser | null) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      apiKey: null,
      user: null,
      hydrated: false,
      setHydrated: (value) => set({ hydrated: value }),
      setSession: ({ token, apiKey, user }) => set({ token, apiKey: apiKey ?? null, user }),
      updateUser: (user) => set({ user }),
      logout: () => set({ token: null, apiKey: null, user: null }),
    }),
    {
      name: "grievance-auth",
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true);
      },
    },
  ),
);

export function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.localStorage.getItem("grievance-auth");
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as { state?: { token?: string | null } };
    return parsed.state?.token ?? null;
  } catch {
    return null;
  }
}
