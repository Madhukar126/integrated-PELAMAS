# POLARIS Demo Script

## 3-minute version
1. Open the judge entry at http://localhost:3000/demo.
2. Explain that the problem is a dependency chain issue rather than isolated inventory tracking.
3. Reset the demo to restore the synthetic baseline.
4. Trigger the eight-day delay scenario and point to Transport T04.
5. Explain the chain: T04 -> C018 -> GF14 -> G07 -> M12.
6. Show the risk event and the recommendation workflow.
7. Summarize why the system is operationally useful even though the dataset is synthetic.

## 5-minute version (primary script)
### 0:00–0:45 | Problem and context
Explain that NCPOR needs decision support for expedition logistics where transport delay can cascade across cargo and asset readiness. POLARIS is designed to show the operational dependency chain and the likely mission consequence before the crisis escalates.

### 0:45–1:30 | Mission control baseline
Open the main dashboard and show the expedition status, cargo status, inventory state, and risk posture. Stress that the system is synthetic but realistic enough to demonstrate the workflow.

### 1:30–2:15 | Trigger the transport delay
Use the simulate delay control. Show the changed transport ETA and the resulting high-risk condition. Explain that this is the same scenario that the system is designed to detect: T04 delayed by eight days.

### 2:15–3:00 | Dependency path and impact
Walk through the dependency chain: Transport T04 -> Cargo C018 -> Inventory GF14 -> Generator G07 -> Mission M12. Emphasize that the issue is not merely cargo movement; it is coordinated mission risk across the chain.

### 3:00–3:45 | Forecasting and shortage logic
Point to the shortage and forecasting output. Explain that the model tracks current stock, reserve threshold, and projected consumption to identify when supply may run below safe limits.

### 3:45–4:30 | Human decision support
Open the recommendation and audit workflow. Show that the system explains the risk and preserves a human approval or rejection action. The decision is recorded in the audit trail.

### 4:30–5:00 | Cargo optimization and impact summary
Run the cargo optimizer and explain how it prioritizes mission-critical cargo under capacity constraints. Close by summarizing that the project improves explainability, early warning, and decision quality without replacing human oversight.

## 8-minute extended version
Use the 5-minute script and expand it with:
- a deeper explanation of inventory threshold logic
- the emergency-center and map representations
- current vs. projected risk score and factor breakdown
- a short discussion of why the system remains prototype-only and synthetic
- a final note on how a real deployment would use operational NCPOR datasets and human review for every critical action

## Repeatable demo flow
1. RESET DEMO
2. Normal Mission Control
3. SIMULATE 8-DAY TRANSPORT DELAY
4. Map update
5. Cargo impact
6. Inventory shortage prediction
7. Generator G07 impact
8. Mission M12 impact
9. Dependency graph
10. Recommendation approval or rejection
11. Emergency Center
12. RUN CARGO OPTIMIZATION
13. Final dashboard summary
