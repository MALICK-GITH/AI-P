from __future__ import annotations

import logging
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple, Optional
from functools import lru_cache
from datetime import datetime, timedelta
import pandas as pd

from app.core.model_loader import ModelRegistry
from app.services.feature_builder import FeatureBuilder, FeatureVector
from app.services.model_router import ModelRouter
from app.services.feature_adapter import FeatureAdapter
from app.schemas.request_schema import PredictionRequest

logger = logging.getLogger(__name__)


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


class PredictionCache:
    """
    SOLITAIRE HACK: Cache intelligent avec TTL pour les prédictions
    Optimise les performances en évitant les recalculs pour les requêtes similaires.
    """
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self._cache: Dict[str, Tuple[dict, datetime]] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, request: PredictionRequest, endpoint: str) -> str:
        """Génère une clé unique basée sur les paramètres de requête"""
        request_dict = {
            "endpoint": endpoint,
            "league": request.league,
            "home_team": request.home_team,  # SOLITAIRE HACK: Utiliser le nom réel du champ
            "away_team": request.away_team,  # SOLITAIRE HACK: Utiliser le nom réel du champ
            "home_odds": request.home_odds,
            "draw_odds": request.draw_odds,
            "away_odds": request.away_odds,
            "game_mode": getattr(request, 'game_mode', None),
            "game_version": getattr(request, 'game_version', None),
        }
        # Hash les données pour créer une clé compacte
        request_str = json.dumps(request_dict, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def get(self, request: PredictionRequest, endpoint: str) -> Optional[dict]:
        """Récupère une prédiction du cache si disponible et non expirée"""
        key = self._generate_key(request, endpoint)
        
        if key in self._cache:
            result, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self._ttl_seconds):
                self._hits += 1
                logger.debug(f"Cache hit for key {key} (hits: {self._hits}, misses: {self._misses})")
                return result
            else:
                # Entrée expirée, supprimer
                del self._cache[key]
        
        self._misses += 1
        return None
    
    def set(self, request: PredictionRequest, endpoint: str, result: dict) -> None:
        """Stocke une prédiction dans le cache"""
        # Nettoyer le cache si nécessaire (LRU simple)
        if len(self._cache) >= self._max_size:
            # Supprimer l'entrée la plus ancienne (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        key = self._generate_key(request, endpoint)
        self._cache[key] = (result, datetime.now())
        logger.debug(f"Cache set for key {key} (cache size: {len(self._cache)})")
    
    def clear(self) -> None:
        """Vide le cache"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "ttl_seconds": self._ttl_seconds,
        }


@dataclass(frozen=True)
class ModelPrediction:
    model_name: str
    value: Any
    probabilities: Dict[str, float] | None = None


class FusionEngine:
    def __init__(self, registry: ModelRegistry, feature_builder: FeatureBuilder, enable_cache: bool = True) -> None:
        self._registry = registry
        self._feature_builder = feature_builder
        # SOLITAIRE HACK: Intégration du système de routage intelligent
        self._model_router = ModelRouter(registry)
        # SOLITAIRE HACK: Activation du cache intelligent pour optimiser les performances
        self._cache = PredictionCache() if enable_cache else None
        self._enable_cache = enable_cache

    def build_features(self, request: PredictionRequest) -> FeatureVector:
        return self._feature_builder.build_vector(request)

    def _predict_raw(self, model_name: str, features: FeatureVector) -> ModelPrediction:
        """
        SOLITAIRE HACK: Version adaptée pour gérer les modèles avec des features différentes.
        Utilise le routage intelligent si le modèle spécifié n'est pas trouvé.
        Adapte les features pour les modèles .pkl spécifiques.
        """
        # SOLITAIRE HACK: Si le modèle n'existe pas, utiliser le routage intelligent
        if model_name not in self._registry.artifacts:
            logger.warning(f"Model {model_name} not found, using router fallback")
            model_name = self._model_router.select_model_for_context(fallback=None)
            if not model_name:
                raise ValueError(f"No models available in registry")
                
        artifact = self._registry.get(model_name)
        
        # SOLITAIRE HACK: Déterminer si c'est un modèle .pkl spécifique
        is_specific_pkl = (
            model_name.endswith('.pkl') and 
            artifact.bundle.get('original_format') == 'specific_pkl'
        )
        
        # SOLITAIRE HACK: Gestion des features dynamiques
        try:
            if is_specific_pkl:
                # Pour les modèles .pkl spécifiques, adapter les features
                logger.info(f"Adapting features for specific .pkl model: {model_name}")
                system_features_dict = features.to_dict()
                pkl_features_dict = FeatureAdapter.adapt_features(system_features_dict)
                
                # Créer le DataFrame avec les features attendues par le modèle
                target_features = list(artifact.feature_columns)
                payload = pd.DataFrame([pkl_features_dict])
                
                # S'assurer que l'ordre des colonnes correspond
                payload = payload[target_features]
            else:
                # Pour les modèles standards, utiliser les features normales
                payload = features.to_frame(artifact.feature_columns)
                
        except Exception as e:
            logger.warning(f"Feature mismatch for {model_name}, using default features: {e}")
            # Fallback aux features par défaut
            payload = features.to_frame(None)
            
        model = artifact.model
        
        # SOLITAIRE HACK: Gestion des erreurs de prédiction
        try:
            prediction = model.predict(payload)[0]
        except Exception as e:
            logger.error(f"Prediction failed for {model_name}: {e}")
            # Essayer avec un autre modèle via le routeur
            fallback_model = self._model_router.select_model_for_context(fallback=None)
            if fallback_model and fallback_model != model_name:
                logger.info(f"Retrying with fallback model: {fallback_model}")
                return self._predict_raw(fallback_model, features)
            raise

        probabilities = None
        if hasattr(model, "predict_proba"):
            try:
                proba = model.predict_proba(payload)[0]
                classes = [str(item) for item in getattr(model, "classes_", [])]
                probabilities = {label: float(score) for label, score in zip(classes, proba)}
            except Exception as e:
                logger.warning(f"predict_proba failed for {model_name}: {e}")

        return ModelPrediction(model_name=model_name, value=prediction, probabilities=probabilities)
    
    def _select_model_for_request(self, request: PredictionRequest, default_model: str) -> str:
        """
        SOLITAIRE HACK: Sélectionne intelligemment le modèle selon le contexte de la requête.
        """
        # Essayer d'abord le modèle par défaut s'il existe
        if default_model in self._registry.artifacts:
            return default_model
            
        # Sinon, utiliser le routage intelligent
        return self._model_router.select_model_for_context(
            league=getattr(request, 'league', None),
            game_mode=getattr(request, 'game_mode', None),
            game_version=getattr(request, 'game_version', None),
        )

    def predict_over_under(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        # SOLITAIRE HACK: Vérifier le cache d'abord
        if self._enable_cache and self._cache:
            cached_result = self._cache.get(request, "over_under")
            if cached_result:
                return cached_result
        
        vector = features or self.build_features(request)
        # SOLITAIRE HACK: Utiliser le routage intelligent pour la sélection de modèle
        model_name = self._select_model_for_request(request, "over_under_2.5.joblib")
        prediction = self._predict_raw(model_name, vector)
        over_probability = _probability_for_over(prediction.probabilities, prediction.value)
        label = "OVER" if over_probability >= 0.5 else "UNDER"
        confidence = round(max(over_probability, 1.0 - over_probability) * 100.0, 1)
        
        result = {
            "over_under_2_5": label,
            "confidence": confidence,
            "model_used": model_name,
            "source": "ONE DELUX AI 3.0",  # SOLITAIRE HACK: Mise à jour version
        }
        
        # SOLITAIRE HACK: Stocker dans le cache
        if self._enable_cache and self._cache:
            self._cache.set(request, "over_under", result)
        
        return result

    def predict_home_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        # SOLITAIRE HACK: Vérifier le cache d'abord
        if self._enable_cache and self._cache:
            cached_result = self._cache.get(request, "home_goals")
            if cached_result:
                return cached_result
        
        vector = features or self.build_features(request)
        model_name = self._select_model_for_request(request, "team_home_goals.joblib")
        prediction = self._predict_raw(model_name, vector)
        value = int(_clamp(round(_as_float(prediction.value)), 0, 20))
        
        result = {
            "home_goals": value,
            "model_used": model_name,
            "source": "ONE DELUX AI 3.0",  # SOLITAIRE HACK: Mise à jour version
        }
        
        # SOLITAIRE HACK: Stocker dans le cache
        if self._enable_cache and self._cache:
            self._cache.set(request, "home_goals", result)
        
        return result

    def predict_away_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        # SOLITAIRE HACK: Vérifier le cache d'abord
        if self._enable_cache and self._cache:
            cached_result = self._cache.get(request, "away_goals")
            if cached_result:
                return cached_result
        
        vector = features or self.build_features(request)
        model_name = self._select_model_for_request(request, "team_away_goals.joblib")
        prediction = self._predict_raw(model_name, vector)
        value = int(_clamp(round(_as_float(prediction.value)), 0, 20))
        
        result = {
            "away_goals": value,
            "model_used": model_name,
            "source": "ONE DELUX AI 3.0",  # SOLITAIRE HACK: Mise à jour version
        }
        
        # SOLITAIRE HACK: Stocker dans le cache
        if self._enable_cache and self._cache:
            self._cache.set(request, "away_goals", result)
        
        return result

    def predict_total_goals(self, request: PredictionRequest, features: FeatureVector | None = None) -> dict[str, Any]:
        # SOLITAIRE HACK: Vérifier le cache d'abord
        if self._enable_cache and self._cache:
            cached_result = self._cache.get(request, "total_goals")
            if cached_result:
                return cached_result
        
        vector = features or self.build_features(request)
        model_name = self._select_model_for_request(request, "match_total_goals.joblib")
        prediction = self._predict_raw(model_name, vector)
        value = int(_clamp(round(_as_float(prediction.value)), 0, 40))
        
        result = {
            "total_goals": value,
            "model_used": model_name,
            "source": "ONE DELUX AI 3.0",  # SOLITAIRE HACK: Mise à jour version
        }
        
        # SOLITAIRE HACK: Stocker dans le cache
        if self._enable_cache and self._cache:
            self._cache.set(request, "total_goals", result)
        
        return result

    def predict_fusion(self, request: PredictionRequest) -> dict[str, Any]:
        # SOLITAIRE HACK: Vérifier le cache d'abord
        if self._enable_cache and self._cache:
            cached_result = self._cache.get(request, "fusion")
            if cached_result:
                return cached_result
        
        features = self.build_features(request)

        # SOLITAIRE HACK: Utiliser le routage intelligent pour chaque prédiction
        home_model = self._select_model_for_request(request, "team_home_goals.joblib")
        away_model = self._select_model_for_request(request, "team_away_goals.joblib")
        total_model = self._select_model_for_request(request, "match_total_goals.joblib")
        over_under_model = self._select_model_for_request(request, "over_under_2.5.joblib")

        home_prediction = self._predict_raw(home_model, features)
        away_prediction = self._predict_raw(away_model, features)
        total_prediction = self._predict_raw(total_model, features)
        over_under_prediction = self._predict_raw(over_under_model, features)

        home_goals = int(_clamp(round(_as_float(home_prediction.value)), 0, 20))
        away_goals = int(_clamp(round(_as_float(away_prediction.value)), 0, 20))
        total_goals_model = int(_clamp(round(_as_float(total_prediction.value)), 0, 40))
        score_total = home_goals + away_goals

        over_probability = _probability_for_over(over_under_prediction.probabilities, over_under_prediction.value)
        over_under_label = "OVER" if over_probability >= 0.5 else "UNDER"

        model_alignment = 1.0 - min(abs(total_goals_model - score_total) / max(float(max(total_goals_model, score_total, 1)), 1.0), 1.0)
        over_support = max(over_probability, 1.0 - over_probability)
        confidence = round(_clamp((0.65 * over_support + 0.35 * model_alignment) * 100.0, 0.0, 100.0), 1)

        result = {
            "home_goals": home_goals,
            "away_goals": away_goals,
            "total_goals": score_total,
            "over_under_2_5": over_under_label,
            "score_prediction": f"{home_goals}-{away_goals}",
            "confidence": confidence,
            "models_used": {
                "home_goals": home_model,
                "away_goals": away_model,
                "total_goals": total_model,
                "over_under": over_under_model,
            },
            "source": "ONE DELUX AI 3.0",  # SOLITAIRE HACK: Mise à jour version
        }
        
        # SOLITAIRE HACK: Stocker dans le cache
        if self._enable_cache and self._cache:
            self._cache.set(request, "fusion", result)
        
        return result
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        SOLITAIRE HACK: Retourne les statistiques de performance du cache.
        Utile pour le monitoring et l'optimisation.
        """
        if not self._enable_cache or not self._cache:
            return {"cache_enabled": False}
        return self._cache.get_stats()
    
    def clear_cache(self) -> None:
        """
        SOLITAIRE HACK: Vide le cache de prédictions.
        Utile pour forcer un recalcul après une mise à jour de modèles.
        """
        if self._enable_cache and self._cache:
            self._cache.clear()
            logger.info("Prediction cache cleared")
