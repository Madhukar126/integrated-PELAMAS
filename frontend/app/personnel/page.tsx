import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Personnel"
      subtitle="Crew and field teams are assigned to mission-critical tasks with safety, fatigue, and deployment coverage tracked daily."
      items={[
        { label: "Deployed", value: "30", tone: "cyan" },
        { label: "Status", value: "Ready", tone: "emerald" },
        { label: "Exposure", value: "Moderate", tone: "amber" },
      ]}
      notes={[
        "Personnel rotation remains stable across both field sites.",
        "A logistics slowdown increases the importance of maintaining crew effectiveness and task continuity.",
        "Safety and fatigue controls should remain strict while mission operations continue.",
      ]}
    />
  );
}
