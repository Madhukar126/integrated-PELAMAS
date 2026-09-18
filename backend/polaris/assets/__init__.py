try:
    from backend.polaris.assets.asset_risk_model import AssetRiskModel
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.assets.asset_risk_model import AssetRiskModel

__all__ = ["AssetRiskModel"]
