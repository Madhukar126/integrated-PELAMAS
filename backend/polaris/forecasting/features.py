from __future__ import annotations

from statistics import mean


def build_demand_feature_rows(history: list[float]) -> list[list[float]]:
    if len(history) < 3:
        return [[float(value)] for value in history]

    rows: list[list[float]] = []
    for idx in range(2, len(history)):
        lookback = history[max(0, idx - 7):idx]
        slope = history[idx - 1] - history[idx - 2] if idx >= 2 else 0.0
        rows.append([
            float(history[idx - 1]),
            float(history[idx - 2]),
            float(mean(lookback)) if lookback else float(history[idx - 1]),
            float(slope),
        ])
    return rows


def build_demand_targets(history: list[float]) -> list[float]:
    if len(history) < 3:
        return [float(value) for value in history]
    return [float(history[idx]) for idx in range(2, len(history))]
