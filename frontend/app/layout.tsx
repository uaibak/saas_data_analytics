import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Research SaaS",
  description: "Research-Oriented SaaS Data Analytics Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
