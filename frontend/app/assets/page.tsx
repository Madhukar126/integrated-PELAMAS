import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Assets"
      subtitle="Power, mechanical, and support assets required for safe operations are tracked by condition, usage, and maintenance needs."
      items={[
        { label: "Primary asset", value: "G07", tone: "cyan" },
        { label: "Condition", value: "72%", tone: "amber" },
        { label: "Status", value: "Operating", tone: "emerald" },
      ]}
      notes={[
        "Generator G07 remains operational but is sensitive to downstream supply disruption.",
        "Maintenance planning is aligned with mission priority and inventory support availability.",
        "Asset redundancy remains limited, so service windows require active monitoring.",
      ]}
    />
  );
}
