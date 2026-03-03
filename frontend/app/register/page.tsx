"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import axios from "axios";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { AuthTokenResponse, RegisterPayload } from "@/types/auth";

export default function RegisterPage() {
  const router = useRouter();
  const { isAuthenticated, isInitializing, setToken, initializeAuth } = useAuth();
  const [form, setForm] = useState<RegisterPayload>({
    full_name: "",
    email: "",
    password: "",
    organization_name: "",
  });
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
      const response = await api.post<AuthTokenResponse>("/auth/register", form);
      setToken(response.data.access_token);
      await initializeAuth();
      router.replace("/dashboard");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const message = err.response?.data?.message ?? "Registration failed.";
        setError(message);
      } else {
        setError("Unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-8">
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">Create account</h1>
        <p className="mt-1 text-sm text-slate-500">Start your research workspace.</p>
        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <Input
            label="Full Name"
            required
            value={form.full_name}
            onChange={(e) => setForm((s) => ({ ...s, full_name: e.target.value }))}
          />
          <Input
            label="Organization"
            required
            value={form.organization_name}
            onChange={(e) => setForm((s) => ({ ...s, organization_name: e.target.value }))}
          />
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
            Register
          </Button>
        </form>
        <p className="mt-4 text-sm text-slate-600">
          Already have an account? <Link href="/login" className="text-brand-600 hover:underline">Sign in</Link>
        </p>
      </div>
    </main>
  );
}
