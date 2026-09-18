import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Risk Center"
      subtitle="The risk center consolidates the dependency chain and alerts arising from transport disruption, inventory strain, and asset exposure."
      items={[
        { label: "Risk level", value: "High", tone: "rose" },
        { label: "Trigger", value: "T04 delay", tone: "amber" },
        { label: "Impact", value: "Mission critical", tone: "cyan" },
      ]}
      notes={[
        "The delay on T04 propagates into cargo, inventory, and mission readiness.",
        "The current risk posture is elevated by a shortage in critical supply availability.",
        "Decision support should focus on compensating for the supply gap and protecting mission continuity.",
      ]}
    />
  );
}
