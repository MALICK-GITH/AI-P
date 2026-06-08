from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

import joblib

from app.services.feature_builder import FEATURE_COLUMNS, SafeLabelEncoder


logger = logging.getLogger(__name__)

MODEL_FILES: tuple[str, ...] = (
    "over_under_2.5.joblib",
    "team_home_goals.joblib",
    "team_away_goals.joblib",
    "match_total_goals.joblib",
)


def _register_pickle_compatibility() -> None:
    main_module = sys.modules.get("__main__")
    if main_module is not None and not hasattr(main_module, "SafeLabelEncoder"):
        setattr(main_module, "SafeLabelEncoder", SafeLabelEncoder)


@dataclass(frozen=True)
class LoadedModel:
    name: str
    path: Path
    bundle: Dict[str, Any]
    feature_columns: tuple[str, ...]
    label_encoders: Dict[str, Any] = field(repr=False)
    model_type: str | None
    target: str
    trained_at: str | None
    metrics: Dict[str, Any]
    model_class: str
    n_features_in: int | None
    pipeline_steps: tuple[str, ...] | None

    @property
    def model(self) -> Any:
        return self.bundle["model"]

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "target": self.target,
            "model_type": self.model_type,
            "trained_at": self.trained_at,
            "feature_columns": list(self.feature_columns),
            "encoders": list(self.label_encoders.keys()),
            "metrics": self.metrics,
            "model_class": self.model_class,
            "n_features_in": self.n_features_in,
            "pipeline_steps": list(self.pipeline_steps or []),
        }


@dataclass(frozen=True)
class ModelRegistry:
    models_dir: Path
    artifacts: Dict[str, LoadedModel]
    shared_feature_columns: tuple[str, ...]
    loaded_at: str

    def get(self, model_name: str) -> LoadedModel:
        return self.artifacts[model_name]

    @property
    def model_names(self) -> list[str]:
        return list(self.artifacts.keys())

    @property
    def models_loaded(self) -> int:
        return len(self.artifacts)

    def metadata(self) -> list[Dict[str, Any]]:
        return [self.artifacts[name].metadata() for name in sorted(self.artifacts)]


def _extract_pipeline_steps(model: Any) -> tuple[str, ...] | None:
    steps = getattr(model, "steps", None)
    if not steps:
        return None
    try:
        return tuple(step_name for step_name, _ in steps)
    except Exception:  # pragma: no cover - defensive guard for exotic estimators
        return None


def inspect_model_bundle(path: Path) -> LoadedModel:
    _register_pickle_compatibility()
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or "model" not in bundle:
        raise ValueError(f"Invalid model bundle: {path}")

    model = bundle["model"]
    feature_columns = tuple(bundle.get("feature_columns") or FEATURE_COLUMNS)
    label_encoders = dict(bundle.get("label_encoders") or {})
    model_type = bundle.get("model_type")
    target = str(bundle.get("target", path.stem))
    trained_at = bundle.get("trained_at")
    metrics = {
        key: bundle.get(key)
        for key in ("accuracy", "balanced_accuracy", "mae")
        if key in bundle
    }
    model_class = type(model).__name__
    n_features_in = getattr(model, "n_features_in_", None)
    pipeline_steps = _extract_pipeline_steps(model)

    if n_features_in is not None and int(n_features_in) != len(feature_columns):
        raise ValueError(
            f"Model {path.name} expects {n_features_in} features but bundle declares {len(feature_columns)}"
        )

    return LoadedModel(
        name=path.name,
        path=path,
        bundle=bundle,
        feature_columns=feature_columns,
        label_encoders=label_encoders,
        model_type=model_type,
        target=target,
        trained_at=trained_at,
        metrics=metrics,
        model_class=model_class,
        n_features_in=int(n_features_in) if n_features_in is not None else None,
        pipeline_steps=pipeline_steps,
    )


def _validate_feature_schema(artifacts: Mapping[str, LoadedModel]) -> tuple[str, ...]:
    expected: tuple[str, ...] | None = None
    for artifact in artifacts.values():
        if expected is None:
            expected = artifact.feature_columns
            continue
        if artifact.feature_columns != expected:
            raise ValueError(
                "All loaded models must share the same feature column order. "
                f"Mismatch detected for {artifact.name}."
            )
    return expected or tuple(FEATURE_COLUMNS)


@lru_cache(maxsize=1)
def load_model_registry(models_dir: str) -> ModelRegistry:
    _register_pickle_compatibility()
    base_path = Path(models_dir)
    artifacts: Dict[str, LoadedModel] = {}

    for filename in MODEL_FILES:
        path = base_path / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required model file: {path}")
        artifacts[filename] = inspect_model_bundle(path)

    shared_feature_columns = _validate_feature_schema(artifacts)
    loaded_at = datetime.now(timezone.utc).isoformat()
    return ModelRegistry(
        models_dir=base_path,
        artifacts=artifacts,
        shared_feature_columns=shared_feature_columns,
        loaded_at=loaded_at,
    )


def preload_model_registry(models_dir: str) -> ModelRegistry:
    registry = load_model_registry(models_dir)
    logger.info("Loaded %s models from %s", registry.models_loaded, models_dir)
    return registry
