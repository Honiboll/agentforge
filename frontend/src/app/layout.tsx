import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "AgentForge — AI Agent Orchestration",
  description: "Describe your needs, get a team of specialized AI agents working for you.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-grid antialiased">
        {/* Top nav */}
        <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--bg)]/80 backdrop-blur-md">
          <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
            <a href="/" className="flex items-center gap-2 text-lg font-bold">
              <span className="text-xl">🔥</span>
              <span className="gradient-text">AgentForge</span>
            </a>
            <nav className="flex items-center gap-4 text-sm text-[var(--text-muted)]">
              <a href="/" className="hover:text-white transition-colors">Home</a>
              <a href="/settings" className="hover:text-white transition-colors">Settings</a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-white transition-colors"
              >
                GitHub
              </a>
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}

