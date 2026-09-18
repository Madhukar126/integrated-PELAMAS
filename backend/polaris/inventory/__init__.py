try:
    from backend.polaris.inventory.shortage_predictor import ShortagePredictor
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.inventory.shortage_predictor import ShortagePredictor

__all__ = ["ShortagePredictor"]
