from __future__ import annotations


class RecommendationEngine:
    def generate(self, shortage_result: dict, dependency_graph: dict, risk_score: dict) -> list[dict]:
        recommendations: list[dict] = []
        if shortage_result.get("severity") in {"HIGH RISK", "CRITICAL"}:
            recommendations.append({
                "title": "Prioritize GF14 replacement transport",
                "action": "APPROVE alternate shipment for critical filter supplies.",
                "reason": f"Projected stock depletion occurs before the next resupply window: {shortage_result.get('gap_days')} days of gap.",
                "priority": "HIGH",
                "affected_risk": "Inventory risk",
                "estimated_impact": "Reduces mission outage risk for the generator system.",
                "constraints": ["Must preserve mission-critical operations", "Requires expedition-manager approval"],
            })

        if risk_score.get("overall_score", 0) >= 60:
            recommendations.append({
                "title": "Reduce non-critical consumption",
                "action": "MODIFY field activity schedule to preserve critical inventory.",
                "reason": "The dependency chain is under strain from transport delay and upcoming stock depletion.",
                "priority": "MEDIUM",
                "affected_risk": "Mission impact",
                "estimated_impact": "Maintains reserve buffer through the delayed resupply window.",
                "constraints": ["Keep mission-critical observation window intact"],
            })

        recommendations.append({
            "title": "Review asset maintenance readiness",
            "action": "APPROVE maintenance and condition review for Generator G07.",
            "reason": "Generator health remains a major contributor to the overall risk score.",
            "priority": "MEDIUM",
            "affected_risk": "Asset risk",
            "estimated_impact": "Reduces chance of unplanned downtime during the mission window.",
            "constraints": ["Coordinator approval required"],
        })

        return recommendations
