try:
    from backend.polaris.optimization.cargo_optimizer import CargoOptimizer
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.optimization.cargo_optimizer import CargoOptimizer

__all__ = ["CargoOptimizer"]
