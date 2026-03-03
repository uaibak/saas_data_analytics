"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

import api from "@/lib/api";
import type { User } from "@/types/auth";

type AuthState = {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  initializeAuth: () => Promise<void>;
  logout: () => void;
};

const setAuthCookie = (token: string | null) => {
  if (typeof document === "undefined") return;
  if (token) {
    document.cookie = `access_token=${token}; path=/; max-age=86400; samesite=lax`;
  } else {
    document.cookie = "access_token=; path=/; max-age=0; samesite=lax";
  }
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isInitializing: true,
      setToken: (token) => {
        if (typeof window !== "undefined") {
          if (token) {
            window.localStorage.setItem("access_token", token);
          } else {
            window.localStorage.removeItem("access_token");
          }
        }
        setAuthCookie(token);
        set({ token, isAuthenticated: Boolean(token) });
      },
      setUser: (user) => set({ user }),
      initializeAuth: async () => {
        const token = get().token ?? (typeof window !== "undefined" ? window.localStorage.getItem("access_token") : null);
        if (!token) {
          set({ isInitializing: false, isAuthenticated: false, user: null });
          return;
        }

        try {
          get().setToken(token);
          const response = await api.get<User>("/users/me");
          set({ user: response.data, isAuthenticated: true, isInitializing: false });
        } catch {
          get().logout();
          set({ isInitializing: false });
        }
      },
      logout: () => {
        if (typeof window !== "undefined") {
          window.localStorage.removeItem("access_token");
          window.localStorage.removeItem("auth-store");
        }
        setAuthCookie(null);
        set({ token: null, user: null, isAuthenticated: false, isInitializing: false });
      },
    }),
    {
      name: "auth-store",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);
