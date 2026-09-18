import SharedOpsPage from "../shared-ops-page";

export default function Page() {
  return (
    <SharedOpsPage
      title="Transport"
      subtitle="Route timing, transfer conditions, and convoy criticality are monitored to protect the expedition's material flow."
      items={[
        { label: "Transport ID", value: "T04", tone: "cyan" },
        { label: "Current status", value: "Delayed", tone: "amber" },
        { label: "Delay", value: "8 days", tone: "rose" },
      ]}
      notes={[
        "Transport T04 remains the major dependency risk in the present scenario.",
        "ETA drift is driving a cascading inventory and mission risk exposure.",
        "Alternate routing and replacement planning should be reviewed if the delay extends past the current window.",
      ]}
    />
  );
}
