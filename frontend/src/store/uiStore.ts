"use client";

import { create } from "zustand";

export type Toast = {
  id: string;
  title: string;
  description?: string;
  tone?: "info" | "success" | "error";
};

type UiState = {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;
};

export const useUiStore = create<UiState>((set) => ({
  toasts: [],
  addToast: (toast) =>
    set((state) => ({
      toasts: [...state.toasts, { id: crypto.randomUUID(), tone: "info", ...toast }],
    })),
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    })),
}));
