from __future__ import annotations

from statistics import mean

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

try:
    from backend.polaris.forecasting.features import build_demand_feature_rows, build_demand_targets
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.forecasting.features import build_demand_feature_rows, build_demand_targets


class DemandForecastingEngine:
    """Synthetic demand forecasting engine for expedition inventory planning."""

    def __init__(self, history: list[float] | None = None, horizon_days: int = 30, station: str = "BHARATI", item_code: str = "GF14") -> None:
        self.history = list(history or [112, 108, 104, 99, 95, 94, 90, 88, 86, 82])
        self.horizon_days = horizon_days
        self.station = station
        self.item_code = item_code

    def _moving_average_prediction(self) -> float:
        window = self.history[-7:]
        return float(mean(window)) if window else 0.0

    def forecast(self) -> dict:
        baseline = self._moving_average_prediction()
        model_used = "moving_average"
        prediction = baseline
        metric_value = 0.0
        feature_importance = {"lag_1": 0.35, "lag_2": 0.25, "rolling_mean_7": 0.25, "slope": 0.15}

        if len(self.history) >= 5:
            X = build_demand_feature_rows(self.history)
            y = build_demand_targets(self.history)
            if len(X) >= 2:
                train_X = X[:-1]
                train_y = y[:-1]
                test_X = [X[-1]]
                test_y = [y[-1]]

                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(train_X, train_y)
                prediction = float(model.predict(test_X)[0])
                model_used = "random_forest"
                metric_value = float(mean_absolute_error(test_y, [prediction]))
                feature_importance = {
                    key: round(float(value), 4)
                    for key, value in zip(["lag_1", "lag_2", "rolling_mean_7", "slope"], model.feature_importances_)
                }

        forecast_value = max(0.0, float(prediction))
        confidence = min(0.96, max(0.55, 0.72 + (0.08 if model_used == "random_forest" else 0.0)))

        return {
            "item_code": self.item_code,
            "station": self.station,
            "forecast_horizon_days": self.horizon_days,
            "predicted_consumption": round(forecast_value, 2),
            "model_used": model_used,
            "evaluation_metric": "MAE",
            "metric_value": round(metric_value, 4),
            "confidence_score": round(confidence, 3),
            "feature_importance": feature_importance,
            "explanation": (
                "Synthetic demonstration data — not real NCPOR operational data. "
                f"The {self.item_code} forecast uses a {model_used} model and projects a rolling demand of {forecast_value:.2f} units/day "
                f"over the next {self.horizon_days} days."
            ),
        }
