import React from 'react';
import { Activity, AlertCircle, CheckCircle2, Database, RefreshCw, Server } from 'lucide-react';
import { useHealth } from '../hooks/useHealth';

export const HealthCheck: React.FC = () => {
  const { apiStatus, dbStatus, isLoading, error, refetch } = useHealth();

  const isApiOk = apiStatus === 'ok';
  const isDbOk = dbStatus === 'ok';

  return (
    <div
      id="health-card"
      className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl backdrop-blur-xl sm:p-8"
    >
      <div className="absolute -right-20 -top-20 h-48 w-48 rounded-full bg-indigo-500/10 blur-3xl" />
      <div className="absolute -bottom-20 -left-20 h-48 w-48 rounded-full bg-violet-500/10 blur-3xl" />

      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 ring-1 ring-indigo-500/20">
            <Activity className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">System Connectivity &amp; Health</h2>
            <p className="text-xs text-slate-400">
              Vite dev proxy routed via{' '}
              <code className="rounded bg-slate-800 px-1.5 py-0.5 text-indigo-300">
                http://localhost:8001
              </code>
            </p>
          </div>
        </div>

        <button
          id="refresh-health-button"
          onClick={() => void refetch()}
          disabled={isLoading}
          aria-label="Refresh health check"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-800/80 px-4 py-2 text-xs font-medium text-slate-200 transition-all hover:bg-slate-700/80 hover:text-white disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin text-indigo-400' : ''}`} />
          {isLoading ? 'Checking...' : 'Refresh Status'}
        </button>
      </div>

      {/* Status Grid */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {/* Core API Status */}
        <div
          id="api-health-box"
          className={`group flex items-start gap-4 rounded-xl border p-4 transition-all ${
            isApiOk
              ? 'border-emerald-500/30 bg-emerald-950/20 hover:border-emerald-500/50'
              : 'border-rose-500/30 bg-rose-950/20 hover:border-rose-500/50'
          }`}
        >
          <div
            className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
              isApiOk
                ? 'bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 ring-1 ring-rose-500/20'
            }`}
          >
            <Server className="h-4 w-4" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Core API Endpoint
              </span>
              <span
                id="api-status-badge"
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${
                  isApiOk
                    ? 'bg-emerald-500/10 text-emerald-300 ring-1 ring-emerald-500/30'
                    : 'bg-rose-500/10 text-rose-300 ring-1 ring-rose-500/30'
                }`}
              >
                {isApiOk ? (
                  <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                ) : (
                  <AlertCircle className="h-3 w-3 text-rose-400" />
                )}
                {isApiOk ? 'Operational' : 'Unavailable'}
              </span>
            </div>

            <div className="mt-2">
              <p id="api-status-text" className="text-base font-semibold text-white">
                {isApiOk ? 'API: ok' : `API Error: ${error ?? 'Unable to connect to backend'}`}
              </p>
              <p className="mt-0.5 text-xs text-slate-400">
                Route: <code className="text-slate-300">GET /api/health</code>
              </p>
            </div>
          </div>
        </div>

        {/* Database Status */}
        <div
          id="db-health-box"
          className={`group flex items-start gap-4 rounded-xl border p-4 transition-all ${
            isDbOk
              ? 'border-emerald-500/30 bg-emerald-950/20 hover:border-emerald-500/50'
              : 'border-amber-500/30 bg-amber-950/20 hover:border-amber-500/50'
          }`}
        >
          <div
            className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
              isDbOk
                ? 'bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20'
            }`}
          >
            <Database className="h-4 w-4" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                PostgreSQL Engine
              </span>
              <span
                id="db-status-badge"
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${
                  isDbOk
                    ? 'bg-emerald-500/10 text-emerald-300 ring-1 ring-emerald-500/30'
                    : 'bg-amber-500/10 text-amber-300 ring-1 ring-amber-500/30'
                }`}
              >
                {isDbOk ? (
                  <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                ) : (
                  <AlertCircle className="h-3 w-3 text-amber-400" />
                )}
                {isDbOk ? 'Connected' : 'Pending Service'}
              </span>
            </div>

            <div className="mt-2">
              <p id="db-status-text" className="text-base font-semibold text-white">
                {isDbOk ? 'Database: ok' : `Database: ${dbStatus ?? 'Standby'}`}
              </p>
              <p className="mt-0.5 text-xs text-slate-400">
                Route: <code className="text-slate-300">GET /api/health/db (SELECT 1)</code>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
