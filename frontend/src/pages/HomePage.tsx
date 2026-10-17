import React from 'react';
import { Layers, ShieldCheck, Terminal, Cpu } from 'lucide-react';
import { HealthCheck } from '../components/HealthCheck';

export const HomePage: React.FC = () => {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 px-4 py-12 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl space-y-10">
        {/* Top Navigation / Brand Banner */}
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-lg shadow-indigo-500/25">
              <Layers className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white sm:text-2xl">
                University Learning &amp; Internship Platform
              </h1>
              <p className="text-xs font-medium text-indigo-400">
                Brolf Tech Challenge &bull; Phase 0: Foundation
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-300">
              <span className="h-2 w-2 rounded-full bg-indigo-400 animate-ping" />
              Phase 0 Active
            </span>
          </div>
        </header>

        {/* Hero Section */}
        <section className="text-center sm:text-left space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            System Infrastructure &amp; Verification
          </h2>
          <p className="max-w-2xl text-sm leading-relaxed text-slate-400">
            Welcome to the Phase 0 foundational layer. This phase verifies cross-stack connectivity,
            rigorous typing, automated testing, and developer tooling before domain feature
            implementation.
          </p>
        </section>

        {/* Live Connectivity Test Card */}
        <section aria-labelledby="health-card">
          <HealthCheck />
        </section>

        {/* Tech Stack Pillars */}
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-800/90 bg-slate-900/50 p-5 backdrop-blur-sm">
            <div className="flex items-center gap-2.5 text-indigo-400">
              <Terminal className="h-4 w-4" />
              <h3 className="text-sm font-semibold text-white">Backend Foundation</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-slate-400">
              FastAPI, SQLAlchemy 2 (psycopg 3), Alembic, Pydantic v2, and Pytest with 0 warnings.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800/90 bg-slate-900/50 p-5 backdrop-blur-sm">
            <div className="flex items-center gap-2.5 text-indigo-400">
              <Cpu className="h-4 w-4" />
              <h3 className="text-sm font-semibold text-white">Frontend Foundation</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-slate-400">
              React 18, Vite proxy to port 8001, TypeScript strict (no any), Tailwind CSS, and
              Vitest.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800/90 bg-slate-900/50 p-5 backdrop-blur-sm">
            <div className="flex items-center gap-2.5 text-indigo-400">
              <ShieldCheck className="h-4 w-4" />
              <h3 className="text-sm font-semibold text-white">Code Quality &amp; Rules</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-slate-400">
              Ruff &amp; ESLint + Prettier enforcement, thin routers, server session authority, and
              conventional commits.
            </p>
          </div>
        </section>

        {/* Reviewer Note Footer */}
        <footer className="border-t border-slate-800/80 pt-6 text-center text-xs text-slate-500">
          <p>
            University Learning &amp; Internship Platform &bull; Phase 0 Foundation Complete &bull;
            Ready for Phase 1
          </p>
        </footer>
      </div>
    </main>
  );
};
