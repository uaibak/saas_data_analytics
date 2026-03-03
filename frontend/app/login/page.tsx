"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import axios from "axios";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { AuthTokenResponse, LoginPayload } from "@/types/auth";

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isInitializing, setToken, initializeAuth } = useAuth();
  const [form, setForm] = useState<LoginPayload>({ email: "", password: "" });
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isInitializing && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isInitializing, router]);

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await api.post<AuthTokenResponse>("/auth/login", form);
      setToken(response.data.access_token);
      await initializeAuth();
      router.replace("/dashboard");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const message = err.response?.data?.message ?? "Login failed. Please check your credentials.";
        setError(message);
      } else {
        setError("Unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">Sign in</h1>
        <p className="mt-1 text-sm text-slate-500">Access your analytics workspace.</p>
        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <Input
            label="Email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm((s) => ({ ...s, email: e.target.value }))}
          />
          <Input
            label="Password"
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm((s) => ({ ...s, password: e.target.value }))}
          />
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <Button type="submit" className="w-full" isLoading={loading}>
            Login
          </Button>
        </form>
        <p className="mt-4 text-sm text-slate-600">
          No account? <Link href="/register" className="text-brand-600 hover:underline">Create one</Link>
        </p>
      </div>
    </main>
  );
}
