from __future__ import annotations

from typing import Any, Dict, List

from app.core.model_loader import ModelRegistry
from app.services.feature_builder import FeatureBuilder, FeatureVector
from app.services.fusion_engine import FusionEngine
from app.schemas.request_schema import PredictionRequest


class PredictionService:
    def __init__(self, registry: ModelRegistry) -> None:
        self._registry = registry
        self._feature_builder = FeatureBuilder.from_registry(registry)
        self._fusion_engine = FusionEngine(registry, self._feature_builder)

    @property
    def models_loaded(self) -> int:
        return self._registry.models_loaded

    @property
    def model_names(self) -> list[str]:
        return self._registry.model_names

    def model_metadata(self) -> list[Dict[str, Any]]:
        return self._registry.metadata()

    def build_feature_vector(self, request: PredictionRequest) -> FeatureVector:
        return self._feature_builder.build_vector(request)

    def predict_fusion(self, request: PredictionRequest) -> Dict[str, Any]:
        return self._fusion_engine.predict_fusion(request)

    def predict_over_under(self, request: PredictionRequest, features: FeatureVector | None = None) -> Dict[str, Any]:
        return self._fusion_engine.predict_over_under(request, features)

    def predict_home_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> Dict[str, Any]:
        return self._fusion_engine.predict_home_goals(request, features)

    def predict_away_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> Dict[str, Any]:
        return self._fusion_engine.predict_away_goals(request, features)

    def predict_total_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> Dict[str, Any]:
        return self._fusion_engine.predict_total_goals(request, features)
