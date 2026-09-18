"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function callApi(path: string, method: "GET" | "POST" = "GET") {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Request failed");
  }

  return response.json();
}

export default function JudgeDemoPage() {
  const [status, setStatus] = useState("Ready to demonstrate the POLARIS mission-control flow.");
  const [loading, setLoading] = useState(false);
  const [snapshot, setSnapshot] = useState<Record<string, unknown> | null>(null);

  const runAction = async (label: string, handler: () => Promise<unknown>) => {
    setLoading(true);
    setStatus(`Running: ${label}...`);
    try {
      const result = await handler();
      setSnapshot(result as Record<string, unknown>);
      setStatus(`${label} completed successfully.`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setStatus(`Failed: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-2xl shadow-cyan-950/30">
        <div className="flex flex-col gap-4 border-b border-slate-700 pb-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.42em] text-cyan-400">SIH JUDGE MODE</p>
            <h1 className="mt-3 text-3xl font-bold text-white">POLARIS demo entry point</h1>
          </div>
          <div className="rounded-full border border-cyan-500/40 bg-cyan-500/10 px-4 py-2 text-xs font-medium uppercase tracking-[0.2em] text-cyan-300">
            SYNTHETIC DEMONSTRATION DATA
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-slate-700 bg-slate-950/40 p-5">
            <h2 className="text-lg font-semibold text-white">Problem</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              A delayed transport to Bharati can cascade into cargo disruption, inventory depletion,
              generator degradation, and mission-level risk. POLARIS helps teams understand the dependency chain
              and decide on the right intervention before operational impact spreads.
            </p>

            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <button
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-left text-sm font-medium text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => runAction("Reset demo", () => callApi("/phase4/demo/reset", "POST"))}
                disabled={loading}
              >
                RESET DEMO
              </button>
              <button
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-left text-sm font-medium text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => runAction("Starting demo", () => callApi("/phase1/dashboard"))}
                disabled={loading}
              >
                START DEMO
              </button>
              <button
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-left text-sm font-medium text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => runAction("Simulating delay", () => callApi("/phase1/simulate-delay", "POST"))}
                disabled={loading}
              >
                SIMULATE DELAY
              </button>
              <button
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-left text-sm font-medium text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => runAction("Reviewing impact", () => callApi("/phase4/impact-path"))}
                disabled={loading}
              >
                VIEW IMPACT
              </button>
              <button
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-left text-sm font-medium text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => runAction("Running optimization", () => callApi("/polaris/cargo/optimize"))}
                disabled={loading}
              >
                RUN OPTIMIZATION
              </button>
              <button
                className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-left text-sm font-medium text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => runAction("Opening mission overview", () => callApi("/phase4/overview"))}
                disabled={loading}
              >
                VIEW DASHBOARD
              </button>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-950/40 p-5">
            <h2 className="text-lg font-semibold text-white">Current status</h2>
            <p className="mt-3 rounded-xl border border-cyan-500/30 bg-cyan-500/10 p-3 text-sm text-cyan-100">
              {status}
            </p>

            <div className="mt-6 space-y-3 text-sm text-slate-300">
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span>Expedition</span>
                <span className="font-semibold text-white">SIH26062</span>
              </div>
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span>Transport</span>
                <span className="font-semibold text-white">T04</span>
              </div>
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span>Cargo</span>
                <span className="font-semibold text-white">C018</span>
              </div>
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span>Critical inventory</span>
                <span className="font-semibold text-white">GF14</span>
              </div>
              <div className="flex justify-between pb-2">
                <span>Mission</span>
                <span className="font-semibold text-white">M12</span>
              </div>
            </div>
          </div>
        </div>

        {snapshot && (
          <div className="mt-8 rounded-2xl border border-slate-700 bg-slate-950/40 p-5">
            <h2 className="text-lg font-semibold text-white">Latest result</h2>
            <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-xs text-slate-300">
              {JSON.stringify(snapshot, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </main>
  );
}
