export default function DemoModePage() {
  const steps = [
    "View the healthy expedition baseline",
    "Trigger the eight-day transport delay",
    "Confirm POLARIS dependency tracing",
    "Review shortage and inventory risk",
    "Inspect generator risk for G07",
    "Open the recommendation workflow",
    "Approve or reject a recommendation",
    "Run cargo optimization",
    "View the emergency command center",
    "Close the judge walkthrough with the mission impact summary",
  ];

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-10 text-slate-100">
      <div className="mx-auto max-w-5xl rounded-2xl border border-slate-700 bg-slate-900 p-6">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-400">SIH DEMO MODE</p>
        <h1 className="mt-3 text-3xl font-bold text-white">Mission Control judge walkthrough</h1>
        <p className="mt-3 max-w-2xl text-sm text-slate-300">
          This mode follows the deterministic POLARIS demo: a healthy expedition transitions into a transport delay, risk detection, dependency analysis, recommendation review, and cargo optimization.
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {steps.map((step, index) => (
            <div key={step} className="rounded-xl border border-slate-700 bg-slate-950/40 p-4">
              <p className="text-[10px] uppercase tracking-[0.22em] text-slate-400">STEP {index + 1}</p>
              <p className="mt-2 text-lg font-semibold text-white">{step}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
