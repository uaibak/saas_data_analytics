"use client";

import { useEffect } from "react";

import { useAuthStore } from "@/store/authStore";

export const useAuth = () => {
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isInitializing = useAuthStore((s) => s.isInitializing);
  const setToken = useAuthStore((s) => s.setToken);
  const setUser = useAuthStore((s) => s.setUser);
  const initializeAuth = useAuthStore((s) => s.initializeAuth);
  const logout = useAuthStore((s) => s.logout);

  useEffect(() => {
    if (isInitializing) {
      void initializeAuth();
    }
  }, [isInitializing, initializeAuth]);

  return { token, user, isAuthenticated, isInitializing, setToken, setUser, initializeAuth, logout };
};
