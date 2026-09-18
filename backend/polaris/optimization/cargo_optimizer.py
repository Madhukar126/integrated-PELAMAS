from __future__ import annotations

from ortools.sat.python import cp_model


class CargoOptimizer:
    """Cargo loading optimization using CP-SAT with a deterministic objective function."""

    def __init__(self, weight_capacity: float, volume_capacity: float, cargo: list[dict]) -> None:
        self.weight_capacity = float(weight_capacity)
        self.volume_capacity = float(volume_capacity)
        self.cargo = cargo

    def optimize(self) -> dict:
        model = cp_model.CpModel()
        selected = {}
        for idx, item in enumerate(self.cargo):
            selected[idx] = model.NewBoolVar(f"x_{idx}")

        weight_limit = int(round(self.weight_capacity))
        volume_limit = int(round(self.volume_capacity))

        model.Add(sum(int(round(float(item["weight_kg"]))) * selected[idx] for idx, item in enumerate(self.cargo)) <= weight_limit)
        model.Add(sum(int(round(float(item["volume_m3"]))) * selected[idx] for idx, item in enumerate(self.cargo)) <= volume_limit)

        score_terms = []
        for idx, item in enumerate(self.cargo):
            urgency = max(0, 30 - float(item.get("required_by_days", 10)))
            value = (
                float(item.get("criticality", 1)) * 40
                + float(item.get("shortage_risk", 0.0)) * 100
                + float(item.get("mission_impact", 1)) * 20
                + urgency * 2
            )
            score_terms.append(value * selected[idx])

        model.Maximize(sum(score_terms))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 5
        status = solver.Solve(model)

        selected_ids: list[str] = []
        deferred_ids: list[str] = []
        total_weight = 0.0
        total_volume = 0.0
        selected_summary: list[dict] = []

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for idx, item in enumerate(self.cargo):
                chosen = solver.Value(selected[idx]) == 1
                if chosen:
                    selected_ids.append(str(item["id"]))
                    total_weight += float(item["weight_kg"])
                    total_volume += float(item["volume_m3"])
                    selected_summary.append({
                        "id": str(item["id"]),
                        "reason": (
                            f"High criticality ({item.get('criticality', 1)}) and shortage pressure ({item.get('shortage_risk', 0.0)}) "
                            f"support early loading for mission continuity."
                        )
                    })
                else:
                    deferred_ids.append(str(item["id"]))
        else:
            # deterministic fallback for solver failures
            ranked = sorted(
                self.cargo,
                key=lambda item: (
                    float(item.get("criticality", 1))
                    + float(item.get("shortage_risk", 0.0))
                    + float(item.get("mission_impact", 1))
                ),
                reverse=True,
            )
            remaining_weight = self.weight_capacity
            remaining_volume = self.volume_capacity
            for item in ranked:
                if float(item["weight_kg"]) <= remaining_weight and float(item["volume_m3"]) <= remaining_volume:
                    selected_ids.append(str(item["id"]))
                    remaining_weight -= float(item["weight_kg"])
                    remaining_volume -= float(item["volume_m3"])
                    total_weight += float(item["weight_kg"])
                    total_volume += float(item["volume_m3"])
                    selected_summary.append({
                        "id": str(item["id"]),
                        "reason": "Fallback allocation prioritized mission-critical items at the highest value-to-capacity ratio.",
                    })
                else:
                    deferred_ids.append(str(item["id"]))

        for item in self.cargo:
            if str(item["id"]) not in selected_ids and str(item["id"]) in deferred_ids:
                continue

        return {
            "selected_ids": selected_ids,
            "deferred_ids": deferred_ids,
            "total_weight_kg": round(total_weight, 2),
            "total_volume_m3": round(total_volume, 2),
            "weight_capacity": round(self.weight_capacity, 2),
            "volume_capacity": round(self.volume_capacity, 2),
            "weight_utilization_pct": round((total_weight / self.weight_capacity) * 100, 2) if self.weight_capacity else 0.0,
            "volume_utilization_pct": round((total_volume / self.volume_capacity) * 100, 2) if self.volume_capacity else 0.0,
            "objective_value": round(float(sum((float(item.get("criticality", 1)) * 40 + float(item.get("shortage_risk", 0.0)) * 100 + float(item.get("mission_impact", 1)) * 20) for item in self.cargo if str(item["id"]) in selected_ids)), 2),
            "selected_summary": selected_summary,
            "explanation": (
                "Synthetic demonstration data — not real NCPOR operational data. "
                f"The optimizer selected {len(selected_ids)} cargo items to maximize mission value while staying within {self.weight_capacity} kg and {self.volume_capacity} m3 capacity."
            ),
        }
