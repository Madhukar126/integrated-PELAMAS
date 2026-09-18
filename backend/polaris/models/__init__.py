try:
    from backend.polaris.models.model_registry import ModelRegistry, RegisteredModel
except ModuleNotFoundError:  # pragma: no cover - fallback for backend-root execution
    from polaris.models.model_registry import ModelRegistry, RegisteredModel

__all__ = ["ModelRegistry", "RegisteredModel"]
