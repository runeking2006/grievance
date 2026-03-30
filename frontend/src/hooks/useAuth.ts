"use client";

import { useMutation, useQuery, useQueryClient, type UseMutationResult, type UseQueryResult } from "@tanstack/react-query";
import axios from "axios";

import { createToken, fetchMe, registerUser } from "@/api/auth";
import type { AuthUser } from "@/store/authStore";
import { useAuthStore } from "@/store/authStore";
import { useUiStore } from "@/store/uiStore";
import { QUERY_KEYS } from "@/utils/constants";

type LoginPayload = { email: string; apiKey: string };
type RegisterPayload = { email: string; fullName?: string };
type RegisterResult = { registered: AuthUser; token: string };

type UseAuthResult = {
  hydrated: boolean;
  currentUser: AuthUser | null;
  isAuthenticated: boolean;
  loginMutation: UseMutationResult<AuthUser, Error, LoginPayload>;
  registerMutation: UseMutationResult<RegisterResult, Error, RegisterPayload>;
  meQuery: UseQueryResult<AuthUser, Error>;
  signOut: () => void;
};

export function useAuth(): UseAuthResult {
  const queryClient = useQueryClient();
  const addToast = useUiStore((state) => state.addToast);
  const token = useAuthStore((state) => state.token);
  const hydrated = useAuthStore((state) => state.hydrated);
  const setSession = useAuthStore((state) => state.setSession);
  const updateUser = useAuthStore((state) => state.updateUser);
  const logout = useAuthStore((state) => state.logout);

  const meQuery = useQuery<AuthUser, Error>({
    queryKey: QUERY_KEYS.me,
    queryFn: () => fetchMe(),
    enabled: hydrated && Boolean(token),
    retry: false,
  });

  const loginMutation = useMutation<AuthUser, Error, LoginPayload>({
    mutationFn: async (payload) => {
      const tokenResponse = await createToken({
        email: payload.email,
        api_key: payload.apiKey,
      });
      setSession({
        token: tokenResponse.access_token,
        apiKey: payload.apiKey,
        user: { id: "loading", email: payload.email, role: tokenResponse.role },
      });
      const me = await fetchMe(tokenResponse.access_token);
      setSession({
        token: tokenResponse.access_token,
        apiKey: payload.apiKey,
        user: me,
      });
      return me;
    },
    onSuccess: (user) => {
      queryClient.setQueryData(QUERY_KEYS.me, user);
      addToast({ title: "Signed in", description: `Welcome back, ${user.email}.`, tone: "success" });
    },
    onError: (error) => {
      if (axios.isAxiosError(error)) {
        addToast({
          title: "Sign in failed",
          description: error.response?.data?.detail ?? error.message,
          tone: "error",
        });
      }
    },
  });

  const registerMutation = useMutation<RegisterResult, Error, RegisterPayload>({
    mutationFn: async (payload) => {
      const registered = await registerUser({
        email: payload.email,
        full_name: payload.fullName,
      });
      if (!registered.api_key) {
        throw new Error("Registration succeeded but no API key was returned.");
      }
      const tokenResponse = await createToken({
        email: payload.email,
        api_key: registered.api_key,
      });
      const me = await fetchMe(tokenResponse.access_token);
      setSession({
        token: tokenResponse.access_token,
        apiKey: registered.api_key,
        user: me,
      });
      return { registered: me, token: tokenResponse.access_token };
    },
    onSuccess: ({ registered }) => {
      queryClient.setQueryData(QUERY_KEYS.me, registered);
      addToast({
        title: "Account created",
        description: `API key issued for ${registered.email}. Save it for later sign-ins.`,
        tone: "success",
      });
    },
    onError: (error) => {
      if (axios.isAxiosError(error)) {
        addToast({
          title: "Registration failed",
          description: error.response?.data?.detail ?? error.message,
          tone: "error",
        });
      } else if (error instanceof Error) {
        addToast({ title: "Registration failed", description: error.message, tone: "error" });
      }
    },
  });

  const signOut = () => {
    logout();
    queryClient.clear();
    updateUser(null);
    addToast({ title: "Signed out", description: "Session cleared.", tone: "info" });
  };

  return {
    hydrated,
    currentUser: meQuery.data ?? null,
    isAuthenticated: Boolean(token),
    loginMutation,
    registerMutation,
    meQuery,
    signOut,
  };
}
