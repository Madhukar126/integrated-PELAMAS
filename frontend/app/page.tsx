"use client";

import { useEffect, useState } from "react";

type RiskFactor = {
  name: string;
  contribution: number;
  reason: string;
};

type Recommendation = {
  id: string;
  title: string;
  action: string;
  rationale: string;
  status: string;
};

type RiskEvent = {
  id: string;
  event_type: string;
  risk_type: string;
  severity: string;
  score: number;
  title: string;
  description: string;
  explanation: string;
  affected_entities: string[];
  dependency_chain: string[];
  contributing_factors: RiskFactor[];
  created_at?: string;
};

type DashboardState = {
  transport: {
    code: string;
    status: string;
    eta_days: number;
    delay_days: number;
  } | null;
  cargo: {
    code: string;
    item_name: string;
    status: string;
    criticality: string;
    eta_days: number;
  } | null;
  inventory: {
    code: string;
    item_name: string;
    current_quantity: number;
    minimum_stock: number;
    daily_usage: number;
    unit: string;
    available_quantity?: number;
  } | null;
  asset: {
    code: string;
    asset_type: string;
    condition_score: number;
    status: string;
    name?: string;
  } | null;
  mission: {
    code: string;
    name: string;
    status: string;
  } | null;
  risk_event: RiskEvent | null;
  recommendations: Recommendation[];
  normal_state: boolean;
};

type Phase4Overview = {
  expedition: string;
  status: string;
  overall_risk: string;
  risk_score: number;
  last_analysis: string;
  open_critical_alerts: number;
  data_mode: string;
  personnel_deployed: number;
  cargo_in_transit: number;
  delayed_cargo: number;
  critical_inventory: number;
  active_asset_risks: number;
  open_incidents: number;
};

type NotificationItem = {
  id: string;
  category: string;
  title: string;
  message: string;
  severity: string;
  target_type: string;
  target_id: string;
  acknowledged: boolean;
};

type MapData = {
  stations: Array<{ id: string; name: string; x: number; y: number; status: string; type: string }>;
  routes: Array<{ from: string; to: string; type: string; status: string }>;
  markers: Array<{ id: string; name: string; type: string; x: number; y: number; status: string }>;
  layers: string[];
};

type GraphNode = {
  id: string;
  label: string;
  type: string;
  status: string;
  risk: string;
};

type GraphEdge = {
  source: string;
  target: string;
  type: string;
};

type DependencyGraph = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

const defaultState: DashboardState = {
  transport: {
    code: "T04",
    status: "IN_TRANSIT",
    eta_days: 7,
    delay_days: 0,
  },
  cargo: {
    code: "C018",
    item_name: "Generator Filter GF14",
    status: "IN_TRANSIT",
    criticality: "CRITICAL",
    eta_days: 7,
  },
  inventory: {
    code: "GF14",
    item_name: "Generator Filter GF14",
    current_quantity: 8,
    minimum_stock: 12,
    daily_usage: 1.5,
    unit: "unit",
    available_quantity: 6,
  },
  asset: {
    code: "G07",
    asset_type: "Generator",
    condition_score: 72,
    status: "OPERATING",
    name: "Generator G07",
  },
  mission: {
    code: "M12",
    name: "Atmospheric Observation",
    status: "ACTIVE",
  },
  risk_event: null,
  recommendations: [],
  normal_state: true,
};

const defaultOverview: Phase4Overview = {
  expedition: "SIH26062",
  status: "ACTIVE",
  overall_risk: "NORMAL",
  risk_score: 0,
  last_analysis: "2 minutes ago",
  open_critical_alerts: 0,
  data_mode: "SYNTHETIC DEMO",
  personnel_deployed: 30,
  cargo_in_transit: 18,
  delayed_cargo: 0,
  critical_inventory: 8,
  active_asset_risks: 2,
  open_incidents: 0,
};

const defaultMapData: MapData = {
  stations: [
    { id: "GOA", name: "NCPOR Goa", x: 12, y: 28, status: "ACTIVE", type: "STATION" },
    { id: "CAPE_TOWN", name: "Cape Town", x: 32, y: 28, status: "ACTIVE", type: "STATION" },
    { id: "MAITRI", name: "Maitri", x: 68, y: 58, status: "ACTIVE", type: "STATION" },
    { id: "BHARATI", name: "Bharati", x: 82, y: 46, status: "HIGH_RISK", type: "STATION" },
  ],
  routes: [
    { from: "GOA", to: "CAPE_TOWN", type: "LOGISTICS", status: "ACTIVE" },
    { from: "CAPE_TOWN", to: "BHARATI", type: "TRANSPORT", status: "DELAYED" },
    { from: "CAPE_TOWN", to: "MAITRI", type: "TRANSPORT", status: "ACTIVE" },
    { from: "MAITRI", to: "BHARATI", type: "LOGISTICS", status: "ACTIVE" },
  ],
  markers: [
    { id: "T04", name: "Transport T04", type: "SHIP", x: 56, y: 35, status: "DELAYED" },
    { id: "C018", name: "Cargo C018", type: "CARGO", x: 72, y: 40, status: "AFFECTED" },
    { id: "G07", name: "Generator G07", type: "ASSET", x: 84, y: 53, status: "ELEVATED" },
    { id: "M12", name: "Mission M12", type: "MISSION", x: 86, y: 36, status: "AT_RISK" },
  ],
  layers: ["Stations", "Transport", "Cargo", "Personnel", "Risks", "Incidents"],
};

const defaultNotifications: NotificationItem[] = [
  {
    id: "n-001",
    category: "CRITICAL",
    title: "GF14 shortage risk detected at Bharati",
    message: "Current reserve margin remains below the mission threshold.",
    severity: "CRITICAL",
    target_type: "inventory",
    target_id: "GF14",
    acknowledged: false,
  },
  {
    id: "n-002",
    category: "WARNING",
    title: "Transport T04 delayed by 8 days",
    message: "ETA has shifted and cargo criticality has increased.",
    severity: "HIGH",
    target_type: "transport",
    target_id: "T04",
    acknowledged: false,
  },
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export default function Home() {
  const [data, setData] = useState<DashboardState>(defaultState);
  const [overview, setOverview] = useState<Phase4Overview>(defaultOverview);
  const [mapData, setMapData] = useState<MapData>(defaultMapData);
  const [notifications, setNotifications] = useState<NotificationItem[]>(defaultNotifications);
  const [dependencyGraph, setDependencyGraph] = useState<DependencyGraph>({
    nodes: [
      { id: "T04", label: "Transport T04", type: "TRANSPORT", status: "DELAYED", risk: "HIGH" },
      { id: "C018", label: "Cargo C018", type: "CARGO", status: "AFFECTED", risk: "HIGH" },
      { id: "GF14", label: "GF14", type: "ITEM", status: "HIGH RISK", risk: "HIGH" },
      { id: "BHARATI", label: "Bharati Inventory", type: "INVENTORY", status: "HIGH RISK", risk: "HIGH" },
      { id: "G07", label: "Generator G07", type: "ASSET", status: "ELEVATED", risk: "MODERATE" },
      { id: "M12", label: "Mission M12", type: "MISSION", status: "AT RISK", risk: "HIGH" },
    ],
    edges: [
      { source: "T04", target: "C018", type: "DELAY" },
      { source: "C018", target: "GF14", type: "AFFECTS" },
      { source: "GF14", target: "BHARATI", type: "DEPLETES" },
      { source: "BHARATI", target: "G07", type: "IMPACTS" },
      { source: "G07", target: "M12", type: "RISKS" },
    ],
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [resetting, setResetting] = useState(false);

  const loadDashboard = async () => {
    try {
      const [dashboardResponse, overviewResponse, mapResponse, notificationsResponse, graphResponse] = await Promise.all([
        fetch(`${API_BASE}/phase1/dashboard`),
        fetch(`${API_BASE}/phase4/overview`),
        fetch(`${API_BASE}/phase4/map`),
        fetch(`${API_BASE}/phase4/notifications`),
        fetch(`${API_BASE}/polaris/dependency/graph`),
      ]);

      const dashboard = await dashboardResponse.json();
      const overviewData = await overviewResponse.json();
      const mapResponseData = await mapResponse.json();
      const notificationsData = await notificationsResponse.json();
      const graphData = await graphResponse.json();

      setData(dashboard);
      setOverview(overviewData);
      setMapData(mapResponseData);
      setNotifications(Array.isArray(notificationsData) ? notificationsData : defaultNotifications);
      setDependencyGraph(graphData ?? {
        nodes: [],
        edges: [],
      });
    } catch (error) {
      console.error("Failed to load mission-control data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDashboard();
  }, []);

  const simulateDelay = async () => {
    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE}/phase1/simulate-delay`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Simulation request failed");
      }
      await loadDashboard();
    } catch (error) {
      console.error("Delay simulation failed", error);
    } finally {
      setSubmitting(false);
    }
  };

  const resetDemo = async () => {
    setResetting(true);
    try {
      const response = await fetch(`${API_BASE}/phase4/demo/reset`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Demo reset request failed");
      }
      await loadDashboard();
    } catch (error) {
      console.error("Demo reset failed", error);
    } finally {
      setResetting(false);
    }
  };

  const handleDecision = async (recommendationId: string, decision: "APPROVE" | "MODIFY" | "REJECT") => {
    try {
      const response = await fetch(`${API_BASE}/recommendations/${recommendationId}/decision`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          decision,
          comment: `Decision recorded in the UI: ${decision}`,
          user_name: "expedition_manager",
        }),
      });

      if (!response.ok) {
        throw new Error("Audit log request failed");
      }

      await loadDashboard();
    } catch (error) {
      console.error("Failed to save recommendation decision", error);
    }
  };

  const risk = data?.risk_event;
  const riskLevel = overview.overall_risk || (risk ? risk.severity : "NORMAL");
  const riskScore = overview.risk_score || risk?.score || 0;

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="rounded-2xl border border-sky-900/70 bg-slate-900/80 p-6 shadow-xl shadow-sky-950/20">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-cyan-400">POLARIS</p>
              <h1 className="mt-2 text-3xl font-bold text-white">Mission Control: Phase 4 Operations</h1>
              <p className="mt-2 text-sm text-slate-300">Active expedition SIH26062 • Synthetic demo data for judge walkthrough</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={resetDemo}
                disabled={resetting}
                className="rounded-xl border border-slate-600 bg-slate-800 px-4 py-2.5 text-sm font-semibold text-slate-100 transition hover:border-cyan-500 hover:text-cyan-300 disabled:opacity-60"
              >
                {resetting ? "RESETTING..." : "RESET DEMO"}
              </button>
              <button
                type="button"
                onClick={simulateDelay}
                disabled={submitting}
                className="rounded-xl bg-cyan-500 px-5 py-2.5 text-sm font-bold text-slate-950 shadow-lg shadow-cyan-500/30 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? "SIMULATING..." : "SIMULATE 8-DAY TRANSPORT DELAY"}
              </button>
            </div>
          </div>
        </header>

        <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-4">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <div className="rounded-xl border border-slate-700 bg-slate-950/40 p-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-slate-400">EXPEDITION STATUS</p>
              <p className="mt-2 text-lg font-bold text-cyan-300">{overview.status}</p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-950/40 p-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-slate-400">OVERALL RISK</p>
              <p className="mt-2 text-lg font-bold text-rose-300">{riskLevel}</p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-950/40 p-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-slate-400">LAST ANALYSIS</p>
              <p className="mt-2 text-lg font-bold text-white">{overview.last_analysis}</p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-950/40 p-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-slate-400">OPEN CRITICAL ALERTS</p>
              <p className="mt-2 text-lg font-bold text-amber-300">{overview.open_critical_alerts}</p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-950/40 p-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-slate-400">DATA MODE</p>
              <p className="mt-2 text-lg font-bold text-emerald-300">{overview.data_mode}</p>
            </div>
          </div>
        </div>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            { label: "Active Expedition", value: overview.expedition, tone: "cyan" },
            { label: "Personnel Deployed", value: `${overview.personnel_deployed}`, tone: "emerald" },
            { label: "Cargo in Transit", value: `${overview.cargo_in_transit}`, tone: "amber" },
            { label: "Delayed Cargo", value: `${overview.delayed_cargo} days`, tone: "rose" },
          ].map((card) => (
            <div key={card.label} className="rounded-2xl border border-slate-700 bg-slate-900 p-4">
              <p className="text-[10px] uppercase tracking-[0.25em] text-slate-400">{card.label}</p>
              <p className={`mt-3 text-2xl font-bold ${card.tone === "cyan" ? "text-cyan-300" : card.tone === "emerald" ? "text-emerald-300" : card.tone === "amber" ? "text-amber-300" : "text-rose-300"}`}>
                {card.value}
              </p>
            </div>
          ))}
        </section>

        <section className="grid gap-6 2xl:grid-cols-[1.3fr_0.7fr]">
          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Operational status</h2>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${riskLevel === "HIGH" || riskLevel === "CRITICAL" ? "bg-rose-500/20 text-rose-300" : riskLevel === "MODERATE" ? "bg-amber-500/20 text-amber-300" : "bg-emerald-500/20 text-emerald-300"}`}>
                {riskLevel}
              </span>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-xl border border-slate-700 bg-slate-950/45 p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">MISSION RISK</p>
                <p className="mt-3 text-3xl font-bold text-white">{riskScore}</p>
                <p className="text-sm text-slate-300">/ 100</p>
              </div>
              <div className="rounded-xl border border-slate-700 bg-slate-950/45 p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">CRITICAL INVENTORY</p>
                <p className="mt-3 text-3xl font-bold text-white">{overview.critical_inventory}</p>
                <p className="text-sm text-slate-300">units</p>
              </div>
              <div className="rounded-xl border border-slate-700 bg-slate-950/45 p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">ACTIVE ASSET RISKS</p>
                <p className="mt-3 text-3xl font-bold text-white">{overview.active_asset_risks}</p>
                <p className="text-sm text-slate-300">assets</p>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-slate-700 bg-slate-950/45 p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Dependency chain</p>
                <div className="mt-4 flex flex-wrap items-center gap-2 text-sm text-cyan-200">
                  {["T04", "C018", "GF14", "Bharati Inventory", "G07", "M12"].map((item, index, array) => (
                    <span key={item} className="flex items-center gap-2">
                      <span>{item}</span>
                      {index < array.length - 1 && <span className="text-slate-500">→</span>}
                    </span>
                  ))}
                </div>
              </div>
              <div className="rounded-xl border border-slate-700 bg-slate-950/45 p-4">
                <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">Mission link</p>
                <p className="mt-4 text-xl font-semibold text-white">{data.mission?.name ?? "Atmospheric Observation"}</p>
                <p className="mt-1 text-slate-300">Mission {data.mission?.code ?? "M12"} • {data.mission?.status ?? "ACTIVE"}</p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold text-white">Polar logistics map</h2>
            <div className="relative mt-4 h-72 overflow-hidden rounded-2xl border border-slate-700 bg-[radial-gradient(circle_at_center,_rgba(14,116,144,0.28),_rgba(2,6,23,0.95)_58%)]">
              <div className="absolute inset-0 opacity-40" style={{ backgroundImage: "linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px)", backgroundSize: "24px 24px" }} />
              {mapData.stations.map((station) => (
                <div key={station.id} className="absolute -translate-x-1/2 -translate-y-1/2" style={{ left: `${station.x}%`, top: `${station.y}%` }}>
                  <div className={`flex h-4 w-4 items-center justify-center rounded-full border-2 ${station.status === "HIGH_RISK" ? "border-rose-300 bg-rose-500" : "border-cyan-300 bg-cyan-500"}`} />
                  <div className="mt-2 rounded-full border border-slate-700 bg-slate-950/80 px-2 py-0.5 text-[10px] text-slate-100">{station.name}</div>
                </div>
              ))}
              {mapData.markers.map((marker) => (
                <div key={marker.id} className="absolute -translate-x-1/2 -translate-y-1/2" style={{ left: `${marker.x}%`, top: `${marker.y}%` }}>
                  <div className={`flex h-3.5 w-3.5 items-center justify-center rounded-full border-2 ${marker.status === "DELAYED" || marker.status === "AT_RISK" ? "border-amber-300 bg-amber-500" : "border-violet-300 bg-violet-500"}`} />
                </div>
              ))}
              <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full">
                <path d="M 12 28 Q 22 29 32 28" stroke="#38bdf8" strokeWidth="1" fill="none" strokeDasharray="2 1" />
                <path d="M 32 28 Q 45 30 56 35" stroke="#f59e0b" strokeWidth="1.3" fill="none" strokeDasharray="2 1" />
                <path d="M 56 35 Q 72 38 82 46" stroke="#f87171" strokeWidth="1.4" fill="none" />
                <path d="M 68 58 Q 74 54 82 46" stroke="#38bdf8" strokeWidth="1" fill="none" strokeDasharray="2 1" />
              </svg>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-[10px] uppercase tracking-[0.18em] text-slate-300">
              {mapData.layers.map((layer) => (
                <span key={layer} className="rounded-full border border-slate-700 bg-slate-950/50 px-2 py-1">{layer}</span>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold text-white">Impact path</h2>
            <div className="mt-5 space-y-3">
              {[
                { label: "Transport Delay", value: "T04" },
                { label: "Cargo Delay", value: "C018" },
                { label: "Inventory Reserve Breach", value: "GF14" },
                { label: "Asset Availability Risk", value: "G07" },
                { label: "Mission Impact", value: "M12" },
              ].map((step, index, array) => (
                <div key={step.label} className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full border border-cyan-500 bg-cyan-500/10 text-xs font-bold text-cyan-300">{index + 1}</div>
                  <div className="flex-1 rounded-xl border border-slate-700 bg-slate-950/40 p-3">
                    <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">{step.label}</p>
                    <p className="mt-1 font-semibold text-white">{step.value}</p>
                  </div>
                  {index < array.length - 1 && <span className="text-xl text-slate-500">↓</span>}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold text-white">Notification center</h2>
            <div className="mt-4 space-y-3">
              {notifications.map((notification) => (
                <div key={notification.id} className="rounded-xl border border-slate-700 bg-slate-950/45 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`rounded-full px-2 py-1 text-[9px] uppercase tracking-[0.18em] ${notification.category === "CRITICAL" ? "bg-rose-500/20 text-rose-300" : notification.category === "WARNING" ? "bg-amber-500/20 text-amber-300" : "bg-cyan-500/20 text-cyan-300"}`}>
                      {notification.category}
                    </span>
                    <span className="text-[10px] uppercase tracking-[0.18em] text-slate-400">{notification.severity}</span>
                  </div>
                  <p className="mt-3 font-semibold text-white">{notification.title}</p>
                  <p className="mt-1 text-sm text-slate-300">{notification.message}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold text-white">Dependency graph</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {dependencyGraph.nodes.map((node) => (
                <div key={node.id} className="rounded-xl border border-slate-700 bg-slate-950/45 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-white">{node.label}</p>
                    <span className={`rounded-full px-2 py-0.5 text-[9px] uppercase tracking-[0.18em] ${node.risk === "HIGH" ? "bg-rose-500/20 text-rose-300" : "bg-amber-500/20 text-amber-300"}`}>
                      {node.risk}
                    </span>
                  </div>
                  <p className="mt-2 text-[10px] uppercase tracking-[0.18em] text-slate-400">{node.type}</p>
                  <p className="mt-1 text-sm text-slate-300">Status: {node.status}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold text-white">Recommended actions</h2>
            <div className="mt-4 space-y-3">
              {(data.recommendations.length > 0 ? data.recommendations : [
                { id: "r-1", title: "Approve emergency replacement freight", action: "APPROVE_EMERGENCY_REPLACEMENT", rationale: "Protect mission continuity and reduce inventory depletion risk.", status: "OPEN" },
                { id: "r-2", title: "Re-route cargo priority", action: "PRIORITIZE_CRITICAL_CARGO", rationale: "Rebalance the next transport window to protect critical supply delivery.", status: "OPEN" },
              ]).map((item) => (
                <div key={item.id} className="rounded-xl border border-slate-700 bg-slate-950/45 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-white">{item.title}</p>
                    <span className="rounded-full border border-cyan-500/40 bg-cyan-500/10 px-2 py-0.5 text-[9px] uppercase tracking-[0.18em] text-cyan-300">{item.status}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-300">{item.rationale}</p>
                  <div className="mt-3 flex gap-2">
                    {(["APPROVE", "MODIFY", "REJECT"] as const).map((decision) => (
                      <button
                        key={decision}
                        type="button"
                        onClick={() => handleDecision(item.id, decision)}
                        className="rounded-lg border border-slate-600 bg-slate-900 px-2 py-1 text-[10px] font-semibold uppercase text-slate-100 transition hover:border-cyan-500 hover:text-cyan-300"
                      >
                        {decision}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
