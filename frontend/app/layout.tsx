import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Rulebook That Argues With Itself",
  description:
    "An evidence-first university regulation QA system that knows when the rulebook answers, stays silent, or contradicts itself.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
