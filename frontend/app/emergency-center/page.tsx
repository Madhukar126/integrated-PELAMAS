import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Emergency Center"
      subtitle="Emergency response coordination aligns service recovery, safety controls, and escalation triggers for the current expedition scenario."
      items={[
        { label: "Escalation", value: "Level 2", tone: "rose" },
        { label: "Primary cause", value: "Transport delay", tone: "amber" },
        { label: "Response", value: "Active", tone: "emerald" },
      ]}
      notes={[
        "Response planning remains active and centered on maintaining crew safety and mission continuity.",
        "The emergency center should coordinate supply prioritization and asset contingency decisions.",
        "Time-sensitive escalation will increase if the transport delay extends beyond the current plan.",
      ]}
    />
  );
}
