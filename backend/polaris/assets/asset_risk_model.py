from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class AssetRiskModel:
    """Synthetic asset risk model using explainable feature contributions."""

    def __init__(self, random_seed: int = 42) -> None:
        self.random_seed = random_seed
        self.model = self._train_model()

    def _train_model(self) -> RandomForestClassifier:
        records = []
        for idx in range(300):
            operating_hours = 1000 + idx * 4
            age_days = 20 + idx % 120
            maintenance_gap = (idx % 40) + (idx % 7) * 3
            temperature = 55 + (idx % 22) + (idx // 17)
            load = 0.35 + (idx % 10) * 0.04
            faults = 0 if idx % 5 else 2
            risk_score = min(
                1.0,
                0.28 * (operating_hours / 6000)
                + 0.25 * (maintenance_gap / 40)
                + 0.22 * ((temperature - 60) / 35)
                + 0.18 * load
                + 0.07 * (faults / 3),
            )
            label = 1 if risk_score > 0.56 else 0
            records.append([operating_hours, age_days, maintenance_gap, temperature, load, faults, risk_score, label])

        features = [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in records]
        labels = [r[7] for r in records]
        X_train, _, y_train, _ = train_test_split(features, labels, test_size=0.2, random_state=self.random_seed, stratify=labels)
        model = RandomForestClassifier(n_estimators=80, random_state=self.random_seed, max_depth=4)
        model.fit(X_train, y_train)
        return model

    def predict(self, asset: dict) -> dict:
        operating_hours = float(asset.get("operating_hours", 0))
        age_days = float(asset.get("age_days", 30))
        maintenance_gap = float(asset.get("maintenance_gap_days", 0))
        temperature = float(asset.get("temperature_c", 50))
        load = float(asset.get("load_fraction", 0.5))
        faults = float(asset.get("fault_count", 0))

        score = min(
            1.0,
            0.28 * (operating_hours / 6000)
            + 0.25 * (maintenance_gap / 40)
            + 0.22 * max(0.0, (temperature - 60) / 35)
            + 0.18 * load
            + 0.07 * (faults / 3),
        )
        probability = float(self.model.predict_proba([[operating_hours, age_days, maintenance_gap, temperature, load, faults]])[0][1])
        final_score = min(1.0, max(score, probability))

        if final_score >= 0.8:
            severity = "HIGH"
        elif final_score >= 0.6:
            severity = "MODERATE"
        elif final_score >= 0.4:
            severity = "WATCH"
        else:
            severity = "LOW"

        factors = []
        if maintenance_gap > 15:
            factors.append({"name": "maintenance overdue", "weight": 0.32, "reason": "Maintenance gap exceeds the recommended interval."})
        if operating_hours > 4000:
            factors.append({"name": "operating hours", "weight": 0.22, "reason": "High cumulative operating hours increase wear exposure."})
        if temperature > 65:
            factors.append({"name": "temperature trend", "weight": 0.18, "reason": "Elevated thermal load shows an increasing stress indicator."})
        if faults > 0:
            factors.append({"name": "fault count", "weight": 0.12, "reason": "Past fault indicators suggest remaining asset resilience is reduced."})
        if not factors:
            factors.append({"name": "baseline health", "weight": 0.12, "reason": "The asset remains within the normal operating envelope."})

        explanation = (
            "Synthetic demonstration data — not real NCPOR operational data. "
            f"Asset risk score {final_score:.2f} indicates {severity} maintenance risk. The result is driven by maintenance backlog, operating hours, and thermal stress."
        )

        return {
            "risk_score": round(final_score, 3),
            "severity": severity,
            "factors": factors,
            "explanation": explanation,
        }
