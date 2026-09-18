type OpsItem = {
  label: string;
  value: string;
  tone?: "cyan" | "amber" | "rose" | "emerald";
};

type OpsPageProps = {
  title: string;
  subtitle: string;
  items: OpsItem[];
  notes: string[];
};

const toneStyles: Record<NonNullable<OpsItem["tone"]>, string> = {
  cyan: "border-cyan-500/30 bg-cyan-500/10 text-cyan-200",
  amber: "border-amber-500/30 bg-amber-500/10 text-amber-200",
  rose: "border-rose-500/30 bg-rose-500/10 text-rose-200",
  emerald: "border-emerald-500/30 bg-emerald-500/10 text-emerald-200",
};

export default function SharedOpsPage({ title, subtitle, items, notes }: OpsPageProps) {
  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-400">POLARIS</p>
          <h1 className="mt-2 text-3xl font-bold text-white">{title}</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">{subtitle}</p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          {items.map((item) => (
            <div key={item.label} className="rounded-2xl border border-slate-700 bg-slate-900 p-4">
              <p className="text-xs uppercase text-slate-400">{item.label}</p>
              <p className={`mt-3 text-2xl font-semibold ${item.tone ? toneStyles[item.tone] : "text-white"}`}>
                {item.value}
              </p>
            </div>
          ))}
        </section>

        <section className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold text-white">Operational notes</h2>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            {notes.map((note) => (
              <li key={note} className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-cyan-400" />
                <span>{note}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}
