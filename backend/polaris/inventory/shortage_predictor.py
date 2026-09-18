from __future__ import annotations


class ShortagePredictor:
    """Deterministic shortage risk calculation using forecasted consumption and resupply timing."""

    def __init__(
        self,
        available_inventory: float,
        reserved_inventory: float,
        predicted_daily_consumption: float,
        next_resupply_days: float,
        minimum_reserve: float,
    ) -> None:
        self.available_inventory = float(available_inventory)
        self.reserved_inventory = float(reserved_inventory)
        self.predicted_daily_consumption = max(0.001, float(predicted_daily_consumption))
        self.next_resupply_days = float(next_resupply_days)
        self.minimum_reserve = float(minimum_reserve)

    def evaluate(self) -> dict:
        usable_inventory = max(0.0, self.available_inventory - self.reserved_inventory)
        estimated_days_of_supply = usable_inventory / self.predicted_daily_consumption if self.predicted_daily_consumption > 0 else float("inf")
        gap_days = max(0.0, self.next_resupply_days - estimated_days_of_supply)

        if usable_inventory <= self.minimum_reserve or estimated_days_of_supply <= 7:
            severity = "CRITICAL"
        elif estimated_days_of_supply <= 14 or gap_days > 0:
            severity = "HIGH RISK"
        elif estimated_days_of_supply <= 30:
            severity = "WATCH"
        else:
            severity = "SAFE"

        return {
            "station": "BHARATI",
            "available_inventory": round(self.available_inventory, 2),
            "reserved_inventory": round(self.reserved_inventory, 2),
            "usable_inventory": round(usable_inventory, 2),
            "predicted_daily_consumption": round(self.predicted_daily_consumption, 2),
            "estimated_days_of_supply": round(estimated_days_of_supply, 2),
            "next_resupply_days": round(self.next_resupply_days, 2),
            "minimum_reserve": round(self.minimum_reserve, 2),
            "gap_days": round(gap_days, 2),
            "severity": severity,
            "status": severity,
            "explanation": (
                "Synthetic demonstration data — not real NCPOR operational data. "
                f"Current usable stock is {usable_inventory:.0f} units against a predicted consumption of {self.predicted_daily_consumption:.2f}/day. "
                f"Estimated days of supply is {estimated_days_of_supply:.1f} days versus a next resupply in {self.next_resupply_days:.0f} days."
            ),
        }
