from __future__ import annotations


class RiskFusionEngine:
    """Prototype configurable risk fusion model with explainable weighted contributions."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or {
            "inventory": 0.30,
            "transport": 0.25,
            "asset": 0.20,
            "mission": 0.15,
            "environment": 0.10,
        }

    def calculate(
        self,
        inventory_risk: float,
        transport_risk: float,
        asset_risk: float,
        mission_risk: float,
        environment_risk: float,
    ) -> dict:
        contributors = {
            "Inventory risk": inventory_risk,
            "Transport risk": transport_risk,
            "Asset risk": asset_risk,
            "Mission impact": mission_risk,
            "Operational risk": environment_risk,
        }

        overall_score = (
            contributors["Inventory risk"] * self.weights["inventory"]
            + contributors["Transport risk"] * self.weights["transport"]
            + contributors["Asset risk"] * self.weights["asset"]
            + contributors["Mission impact"] * self.weights["mission"]
            + contributors["Operational risk"] * self.weights["environment"]
        )

        if overall_score >= 75:
            severity = "CRITICAL"
        elif overall_score >= 50:
            severity = "HIGH"
        elif overall_score >= 25:
            severity = "MODERATE"
        else:
            severity = "LOW"

        contributor_rows = []
        for label, value in contributors.items():
            key = label.lower().replace(" risk", "").replace(" impact", "").replace(" operational", "environment").replace(" ", "_")
            contributor_rows.append({
                "label": label,
                "value": round(float(value), 2),
                "weight": round(float(self.weights.get(key, 0.0)), 4),
            })

        return {
            "prototype_config": "Prototype configurable risk parameters.",
            "overall_score": round(float(overall_score), 2),
            "severity": severity,
            "contributors": contributor_rows,
            "explanation": (
                "Synthetic demonstration data — not real NCPOR operational data. "
                "The fused risk score combines inventory, transport, asset, mission, and operational conditions into a weighted prototype model."
            ),
        }
