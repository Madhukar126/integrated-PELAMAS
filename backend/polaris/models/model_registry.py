from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RegisteredModel:
    model_id: str
    name: str
    version: str
    type: str
    training_date: str
    features: list[str]
    dataset_type: str
    evaluation_metric: str
    metric_value: float
    status: str = "ACTIVE"
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, RegisteredModel] = {}

    def register(self, model: RegisteredModel) -> RegisteredModel:
        self._models[model.model_id] = model
        return model

    def get_model(self, model_id: str) -> RegisteredModel | None:
        return self._models.get(model_id)

    def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "model_id": model.model_id,
                "name": model.name,
                "version": model.version,
                "type": model.type,
                "training_date": model.training_date,
                "features": model.features,
                "dataset_type": model.dataset_type,
                "evaluation_metric": model.evaluation_metric,
                "metric_value": model.metric_value,
                "status": model.status,
                **model.metadata,
            }
            for model in self._models.values()
        ]

    @staticmethod
    def synthetic_training_timestamp() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
