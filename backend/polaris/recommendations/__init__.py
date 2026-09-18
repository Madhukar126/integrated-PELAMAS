try:
    from backend.polaris.recommendations.recommendation_engine import RecommendationEngine
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.recommendations.recommendation_engine import RecommendationEngine

__all__ = ["RecommendationEngine"]
