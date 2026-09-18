# Judge Q&A

## 1. Why is AI required?
AI is used to identify likely shortages, forecast risk propagation, and prioritize the cargo load when logistical constraints are tight. It helps operators act earlier instead of reacting after failure occurs.

## 2. How is POLARIS different from inventory software?
It connects transport disruption, cargo flow, inventory risk, asset condition, and mission impact into one explainable chain instead of tracking items in isolation.

## 3. Where does the training data come from?
The platform uses synthetic demonstration data in this prototype. It is designed to show logic and workflow rather than claim real-world calibration.

## 4. Why Random Forest?
This prototype does not rely on a black-box model as the source of truth. The risk engine and forecast logic remain deterministic and explainable for demonstration purposes.

## 5. Why OR-Tools?
OR-Tools is used to solve a cargo-prioritization problem under capacity constraints while maximizing mission-critical value.

## 6. What happens if AI prediction is wrong?
Human review remains required. The system presents the explanation and decision path, but a human approves or rejects critical actions.

## 7. How is the risk score calculated?
The system combines dependency evidence, inventory pressure, transport delay, and asset health with weighted factors and produces a final explainable score.

## 8. Why should NCPOR trust it?
It is transparent, auditable, and explainable. The decision chain can be traced from transport event to mission impact.

## 9. Can this work without internet?
Yes, this prototype is designed to operate as a local application stack with PostgreSQL and the FastAPI + Next.js services running in the same environment.

## 10. How do you protect sensitive data?
The system avoids hardcoded secrets and uses environment-based configuration; the current demo output is synthetic and anonymized.

## 11. How can this scale?
The backend is modular and can be extended by adding real station data, new analysis modules, and broader mission scenarios.

## 12. What happens if a transport is delayed?
The dependency chain propagates through cargo, inventory, asset availability, and operational mission risk.

## 13. How do you avoid AI hallucinations?
The assistant layer is constrained to database-derived facts and the tested POLARIS risk outputs. It cannot invent missing operational information.

## 14. What is the novelty?
The novelty is the integrated dependency-aware expedition intelligence workflow, not just dashboarding or inventory tracking.

## 15. How would this integrate with NCPOR systems?
It can be integrated as a decision-support layer that consumes data from station systems and provides explainable operational recommendations.

## 16. How will real data improve the model?
The same logic can be recalibrated with historical delays, actual maintenance records, and real inventory performance data.

## 17. Why is there a demo reset?
The reset ensures a repeatable SIH demonstration and prevents accidental contamination of the demo scenario.

## 18. Does the system allow manual override?
Yes. Recommendations can be approved or rejected, with the decision recorded in audit logs.

## 19. Is the map real?
The map is a synthetic operational visualization intended to explain connection and risk paths rather than provide geospatial production accuracy.

## 20. What is the role of the emergency center?
It consolidates relevant alerts and operational actions into a single place so the expedition team can respond quickly.

## 21. Can the system be deployed locally?
Yes, the project includes startup instructions and a Docker Compose workflow for local and containerized deployment.

## 22. Does the system support auditability?
Yes. All critical decisions are recorded in audit logs with decision metadata.

## 23. What is the main risk chain in the demo?
T04 -> C018 -> GF14 -> G07 -> M12.

## 24. Is the model official?
No. It is a prototype configurable risk model intended for demonstration and decision support, not official thresholding.

## 25. Why is the system still useful even without official thresholds?
It gives a structured, explainable view of consequences, allowing teams to understand the chain of impact before a mission is compromised.
