from __future__ import annotations

from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    home_goals: int = Field(..., ge=0, le=20)
    away_goals: int = Field(..., ge=0, le=20)
    total_goals: int = Field(..., ge=0, le=40)
    over_under_2_5: Literal["OVER", "UNDER"]
    score_prediction: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    source: Literal["ONE DELUX AI 2.0", "ONE DELUX AI 3.0"]
    # SOLITAIRE HACK: Informations sur les modèles utilisés
    models_used: dict[str, str] | None = Field(
        default=None,
        description="Mapping of prediction types to model names used",
    )


class StatusResponse(BaseModel):
    status: Literal["ok"]
    models_loaded: int = Field(..., ge=0)


class ModelInfo(BaseModel):
    name: str
    target: str
    model_type: str | None = None
    trained_at: str | None = None
    feature_columns: list[str]
    encoders: list[str]
    metrics: Dict[str, Any] = Field(default_factory=dict)
    model_class: str | None = None
    n_features_in: int | None = None
    pipeline_steps: list[str] = Field(default_factory=list)


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


class ErrorResponse(BaseModel):
    detail: str
    errors: Dict[str, str] | None = None
