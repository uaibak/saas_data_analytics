"use client";

import { useAuthStore } from "@/store/authStore";

export default function Navbar() {
  const user = useAuthStore((s) => s.user);

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
      <h1 className="text-base font-semibold text-slate-900">Dashboard</h1>
      <div className="text-right text-sm">
        <div className="font-medium text-slate-900">{user?.full_name ?? "User"}</div>
        <div className="text-slate-500">Org: {user?.organization_name ?? "-"}</div>
      </div>
    </header>
  );
}
