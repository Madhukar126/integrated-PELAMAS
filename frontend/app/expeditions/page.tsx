import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Expeditions"
      subtitle="SIH26062 posture across the operating theatre, with current mission sequencing and field readiness tracked in one view."
      items={[
        { label: "Active expedition", value: "SIH26062", tone: "cyan" },
        { label: "Base camp", value: "Maitri", tone: "amber" },
        { label: "Support node", value: "Bharati", tone: "emerald" },
      ]}
      notes={[
        "Cross-station movement remains synchronized between Maitri and Bharati.",
        "The transport delay on T04 is still the primary dependency risk to watch.",
        "Cargo and personnel routing is being monitored in real time as the mission window remains active.",
      ]}
    />
  );
}
