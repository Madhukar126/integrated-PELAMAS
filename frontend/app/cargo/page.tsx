import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Cargo"
      subtitle="Cargo status across the expedition chain, including critical items, transit timing, and material exposure."
      items={[
        { label: "Cargo in transit", value: "C018", tone: "cyan" },
        { label: "Criticality", value: "High", tone: "rose" },
        { label: "Delay", value: "8 days", tone: "amber" },
      ]}
      notes={[
        "C018 is the current recovery anchor for the delayed transport chain.",
        "Critical supplies are being re-prioritized based on mission importance and inventory exposure.",
        "Inbound freight is monitored against required-by dates and station readiness.",
      ]}
    />
  );
}
