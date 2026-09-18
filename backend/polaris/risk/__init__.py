try:
    from backend.polaris.risk.dependency_analyzer import DependencyAnalyzer
    from backend.polaris.risk.risk_fusion import RiskFusionEngine
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.risk.dependency_analyzer import DependencyAnalyzer
    from polaris.risk.risk_fusion import RiskFusionEngine

__all__ = ["DependencyAnalyzer", "RiskFusionEngine"]
