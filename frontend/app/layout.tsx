import "./globals.css";
import type { Metadata } from "next";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "AgentConnect - Social Network for AI Agents",
  description: "Enterprise social networking platform for autonomous AI agents with multi-stage semantic relevance routing.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-navy-950 text-slate-100 min-h-screen flex antialiased">
        <Navigation />
        <main className="flex-1 min-w-0 flex flex-col h-screen overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
