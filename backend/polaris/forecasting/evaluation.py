from __future__ import annotations

from sklearn.metrics import mean_absolute_error, mean_squared_error


def evaluate_regression(actual: list[float], predicted: list[float]) -> dict:
    if not actual or not predicted:
        return {"mae": 0.0, "rmse": 0.0, "mape": 0.0}
    mae = mean_absolute_error(actual, predicted)
    rmse = mean_squared_error(actual, predicted, squared=False)
    mape = 0.0
    if any(value != 0 for value in actual):
        errors = [abs((a - p) / a) for a, p in zip(actual, predicted) if a != 0]
        mape = sum(errors) / len(errors) if errors else 0.0
    return {"mae": float(mae), "rmse": float(rmse), "mape": float(mape)}
