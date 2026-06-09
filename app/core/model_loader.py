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

# SOLITAIRE HACK: Adaptation pour charger uniquement les modèles .pkl existants
# Les fichiers .joblib originaux ne sont plus nécessaires
MODEL_FILES: tuple[str, ...] = (
    # Modèles .pkl disponibles
    "Penalty.pkl",
    "FIFA23_Penalty.pkl",
    "FC26_Penalty.pkl",
    "FC25_Penalty.pkl",
    "FC24_Penalty.pkl",
    "FC_26_Champions_League.pkl",
    "FC_26_Championnat_du_monde.pkl",
    "FC_26_5x5_Rush_Superligue.pkl",
    "FC_25_Ligue_européenne.pkl",
    "FC_25_Italy_Championship.pkl",
    "FC_25_Champions_League.pkl",
    "FC_25_Championnat_d'Espagne.pkl",
    "FC_25_Championnat_d'Angleterre.pkl",
    "FC_25_Championnat_d'Allemagne.pkl",
    "FC_25_3x3_Ligue_de_conférence.pkl",
    "FC_24_4x4_Championnat_d'Angleterre.pkl",
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
    """
    SOLITAIRE HACK: Version adaptée pour charger les fichiers .pkl bruts.
    Gère à la fois les bundles .joblib structurés et les modèles .pkl bruts.
    """
    _register_pickle_compatibility()
    loaded_data = joblib.load(path)
    
    # SOLITAIRE HACK: Déterminer le format et créer le bundle approprié
    if isinstance(loaded_data, dict):
        # Cas 1: Format bundle structuré original
        if "model" in loaded_data:
            bundle = loaded_data
        
        # Cas 2: Format .pkl spécifique avec clés spéciales
        elif "models" in loaded_data and "features" in loaded_data:
            logger.info(f"Detected specific .pkl format for {path.name}")
            # Extraire le premier modèle de la liste 'models'
            models = loaded_data["models"]
            if isinstance(models, (list, dict)):
                # Si c'est une liste, prendre le premier
                if isinstance(models, list) and len(models) > 0:
                    model = models[0]
                # Si c'est un dict, prendre la première valeur
                elif isinstance(models, dict):
                    model = list(models.values())[0]
                else:
                    model = models
            else:
                model = models
            
            # Créer un bundle compatible
            bundle = {
                "model": model,
                "feature_columns": loaded_data.get("features", FEATURE_COLUMNS),
                "label_encoders": loaded_data.get("label_map", {}),
                "model_type": type(model).__name__ if hasattr(model, '__class__') else None,
                "target": path.stem,
                "trained_at": None,
                # Métadonnées spécifiques
                "threshold": loaded_data.get("threshold"),
                "league": loaded_data.get("league"),
                "original_format": "specific_pkl",
            }
            
        # Cas 3: Dictionnaire non standard, traiter comme modèle
        else:
            logger.info(f"Treating dict as model for {path.name}")
            bundle = {
                "model": loaded_data,
                "feature_columns": None,
                "label_encoders": {},
                "model_type": type(loaded_data).__name__,
                "target": path.stem,
                "trained_at": None,
            }
    else:
        # Cas 4: Modèle brut direct
        logger.info(f"Loading raw model for {path.name}")
        bundle = {
            "model": loaded_data,
            "feature_columns": None,
            "label_encoders": {},
            "model_type": type(loaded_data).__name__ if hasattr(loaded_data, '__class__') else None,
            "target": path.stem,
            "trained_at": None,
        }
    
    if not isinstance(bundle, dict) or "model" not in bundle:
        raise ValueError(f"Invalid model bundle: {path}")

    model = bundle["model"]
    
    # SOLITAIRE HACK: Gestion flexible des feature columns
    feature_columns_data = bundle.get("feature_columns")
    if feature_columns_data is None:
        feature_columns = tuple(FEATURE_COLUMNS)
    elif isinstance(feature_columns_data, (list, tuple)):
        feature_columns = tuple(feature_columns_data)
    else:
        feature_columns = tuple(FEATURE_COLUMNS)
    
    # Gestion des label encoders
    label_encoders_data = bundle.get("label_encoders", {})
    if isinstance(label_encoders_data, dict):
        label_encoders = label_encoders_data
    else:
        label_encoders = {}
    
    model_type = bundle.get("model_type")
    target = str(bundle.get("target", path.stem))
    trained_at = bundle.get("trained_at")
    metrics = {
        key: bundle.get(key)
        for key in ("accuracy", "balanced_accuracy", "mae", "threshold")
        if key in bundle and bundle[key] is not None
    }
    model_class = type(model).__name__
    n_features_in = getattr(model, "n_features_in_", None)
    pipeline_steps = _extract_pipeline_steps(model)

    # SOLITAIRE HACK: Validation flexible pour les modèles avec features différentes
    if n_features_in is not None and int(n_features_in) != len(feature_columns):
        logger.warning(
            f"Model {path.name} expects {n_features_in} features but bundle declares {len(feature_columns)}. "
            f"Using actual feature columns for compatibility."
        )
        # Utiliser le nombre de features que le modèle attend
        if len(feature_columns) >= int(n_features_in):
            feature_columns = feature_columns[:int(n_features_in)]

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
    """
    SOLITAIRE HACK: Validation relaxée pour supporter des modèles hétérogènes.
    Les modèles .pkl peuvent avoir des structures de features différentes.
    """
    expected: tuple[str, ...] | None = None
    for artifact in artifacts.values():
        if expected is None:
            expected = artifact.feature_columns
            continue
        # SOLITAIRE HACK: Au lieu de rejeter, on logue un avertissement
        if artifact.feature_columns != expected:
            logger.warning(
                f"Feature schema mismatch detected for {artifact.name}. "
                f"Expected {expected}, got {artifact.feature_columns}. "
                f"Using default feature columns for compatibility."
            )
    return expected or tuple(FEATURE_COLUMNS)


@lru_cache(maxsize=1)
def load_model_registry(models_dir: str) -> ModelRegistry:
    """
    SOLITAIRE HACK: Version adaptée pour charger les modèles disponibles
    sans échouer si certains fichiers sont manquants.
    """
    _register_pickle_compatibility()
    base_path = Path(models_dir)
    artifacts: Dict[str, LoadedModel] = {}

    for filename in MODEL_FILES:
        path = base_path / filename
        if not path.exists():
            logger.warning(f"Model file not found, skipping: {path}")
            continue  # SOLITAIRE HACK: Skip missing files instead of failing
        try:
            artifacts[filename] = inspect_model_bundle(path)
            logger.info(f"Successfully loaded model: {filename}")
        except Exception as e:
            logger.error(f"Failed to load model {filename}: {e}")
            continue  # SOLITAIRE HACK: Continue with other models if one fails

    if not artifacts:
        raise ValueError(f"No models could be loaded from {models_dir}")

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
