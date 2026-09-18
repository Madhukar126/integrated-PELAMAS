try:
    from backend.polaris.explainability.explanations import summarize_risk
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.explainability.explanations import summarize_risk

__all__ = ["summarize_risk"]
