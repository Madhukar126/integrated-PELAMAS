import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Inventory"
      subtitle="The expedition inventory profile highlights stock gaps, reorder pressure, and resilience for essential field items."
      items={[
        { label: "Critical item", value: "GF14", tone: "rose" },
        { label: "Available stock", value: "8 units", tone: "amber" },
        { label: "Minimum stock", value: "12 units", tone: "cyan" },
      ]}
      notes={[
        "GF14 inventory remains below mission-required minimums after the delay impact.",
        "Consumption rate continues to drive a sustained deficit against the operational buffer.",
        "Resupply decisions should prioritize mission-critical assets and time-sensitive maintenance items.",
      ]}
    />
  );
}
