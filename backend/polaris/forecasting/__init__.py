try:
    from backend.polaris.forecasting.demand_forecasting import DemandForecastingEngine
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.forecasting.demand_forecasting import DemandForecastingEngine

__all__ = ["DemandForecastingEngine"]
