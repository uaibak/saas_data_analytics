"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAuthStore } from "@/store/authStore";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "#", label: "Datasets (future)" },
  { href: "#", label: "Experiments (future)" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const logout = useAuthStore((s) => s.logout);

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-slate-200 bg-white p-4">
      <div className="mb-6 text-lg font-semibold text-slate-900">Research SaaS</div>
      <nav className="space-y-1">
        {items.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className={`block rounded-md px-3 py-2 text-sm ${pathname === item.href ? "bg-brand-50 text-brand-700" : "text-slate-700 hover:bg-slate-100"}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <button
        onClick={handleLogout}
        className="mt-auto h-10 rounded-md border border-slate-300 text-sm font-medium text-slate-700 hover:bg-slate-100"
      >
        Logout
      </button>
    </aside>
  );
}
