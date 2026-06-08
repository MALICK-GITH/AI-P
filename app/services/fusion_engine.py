from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from app.core.model_loader import ModelRegistry
from app.services.feature_builder import FeatureBuilder, FeatureVector
from app.schemas.request_schema import PredictionRequest


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _probability_for_over(probabilities: Mapping[str, float] | None, prediction: Any) -> float:
    if probabilities:
        for key in ("1", "OVER", "over", "true", "True"):
            if key in probabilities:
                return _clamp(float(probabilities[key]), 0.0, 1.0)
    return 1.0 if int(prediction) == 1 else 0.0


@dataclass(frozen=True)
class ModelPrediction:
    model_name: str
    value: Any
    probabilities: Dict[str, float] | None = None


class FusionEngine:
    def __init__(self, registry: ModelRegistry, feature_builder: FeatureBuilder) -> None:
        self._registry = registry
        self._feature_builder = feature_builder

    def build_features(self, request: PredictionRequest) -> FeatureVector:
        return self._feature_builder.build_vector(request)

    def _predict_raw(self, model_name: str, features: FeatureVector) -> ModelPrediction:
        artifact = self._registry.get(model_name)
        payload = features.to_frame(artifact.feature_columns)
        model = artifact.model
        prediction = model.predict(payload)[0]

        probabilities = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(payload)[0]
            classes = [str(item) for item in getattr(model, "classes_", [])]
            probabilities = {label: float(score) for label, score in zip(classes, proba)}

        return ModelPrediction(model_name=model_name, value=prediction, probabilities=probabilities)

    def predict_over_under(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        vector = features or self.build_features(request)
        prediction = self._predict_raw("over_under_2.5.joblib", vector)
        over_probability = _probability_for_over(prediction.probabilities, prediction.value)
        label = "OVER" if over_probability >= 0.5 else "UNDER"
        confidence = round(max(over_probability, 1.0 - over_probability) * 100.0, 1)
        return {
            "over_under_2_5": label,
            "confidence": confidence,
            "source": "ONE DELUX AI 2.0",
        }

    def predict_home_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        vector = features or self.build_features(request)
        prediction = self._predict_raw("team_home_goals.joblib", vector)
        value = int(_clamp(round(_as_float(prediction.value)), 0, 20))
        return {
            "home_goals": value,
            "source": "ONE DELUX AI 2.0",
        }

    def predict_away_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        vector = features or self.build_features(request)
        prediction = self._predict_raw("team_away_goals.joblib", vector)
        value = int(_clamp(round(_as_float(prediction.value)), 0, 20))
        return {
            "away_goals": value,
            "source": "ONE DELUX AI 2.0",
        }

    def predict_total_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        vector = features or self.build_features(request)
        prediction = self._predict_raw("match_total_goals.joblib", vector)
        value = int(_clamp(round(_as_float(prediction.value)), 0, 40))
        return {
            "total_goals": value,
            "source": "ONE DELUX AI 2.0",
        }

    def predict_fusion(self, request: PredictionRequest) -> dict[str, Any]:
        features = self.build_features(request)

        home_prediction = self._predict_raw("team_home_goals.joblib", features)
        away_prediction = self._predict_raw("team_away_goals.joblib", features)
        total_prediction = self._predict_raw("match_total_goals.joblib", features)
        over_under_prediction = self._predict_raw("over_under_2.5.joblib", features)

        home_goals = int(_clamp(round(_as_float(home_prediction.value)), 0, 20))
        away_goals = int(_clamp(round(_as_float(away_prediction.value)), 0, 20))
        total_goals_model = int(_clamp(round(_as_float(total_prediction.value)), 0, 40))
        score_total = home_goals + away_goals

        over_probability = _probability_for_over(over_under_prediction.probabilities, over_under_prediction.value)
        over_under_label = "OVER" if over_probability >= 0.5 else "UNDER"

        model_alignment = 1.0 - min(abs(total_goals_model - score_total) / max(float(max(total_goals_model, score_total, 1)), 1.0), 1.0)
        over_support = max(over_probability, 1.0 - over_probability)
        confidence = round(_clamp((0.65 * over_support + 0.35 * model_alignment) * 100.0, 0.0, 100.0), 1)

        return {
            "home_goals": home_goals,
            "away_goals": away_goals,
            "total_goals": score_total,
            "over_under_2_5": over_under_label,
            "score_prediction": f"{home_goals}-{away_goals}",
            "confidence": confidence,
            "source": "ONE DELUX AI 2.0",
        }
