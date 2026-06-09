"""
SOLITAIRE HACK - Routes API pour la gestion du contexte de modèles
Expose les fonctionnalités de routage intelligent et de sélection de modèles.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from typing import Any, Dict

router = APIRouter(prefix="/api/models", tags=["model-context"])


@router.get("/contexts")
def get_available_contexts(request: Request) -> Dict[str, Any]:
    """
    Retourne les contextes disponibles dans les modèles chargés.
    Permet aux clients de connaître les modes de jeu, compétitions, pays et versions disponibles.
    """
    service = request.app.state.prediction_service
    # SOLITAIRE HACK: Accès au routeur via le service de prédiction
    if hasattr(service._fusion_engine, '_model_router'):
        router = service._fusion_engine._model_router
        return router.get_available_contexts()
    return {
        "game_modes": [],
        "competitions": [],
        "countries": [],
        "game_versions": [],
        "total_models": service.models_loaded,
    }


@router.get("/select")
def select_model_for_context(
    request: Request,
    league: str = None,
    game_mode: str = None,
    game_version: str = None
) -> Dict[str, Any]:
    """
    Sélectionne le modèle le plus approprié selon le contexte donné.
    
    Args:
        league: Nom de la ligue/compétition
        game_mode: Mode de jeu (penalty, 3x3, etc.)
        game_version: Version du jeu (FIFA23, FC24, etc.)
    """
    service = request.app.state.prediction_service
    
    if hasattr(service._fusion_engine, '_model_router'):
        router = service._fusion_engine._model_router
        selected_model = router.select_model_for_context(
            league=league,
            game_mode=game_mode,
            game_version=game_version,
        )
        
        return {
            "selected_model": selected_model,
            "context": {
                "league": league,
                "game_mode": game_mode,
                "game_version": game_version,
            },
            "available_models": service.model_names,
        }
    
    # Fallback si le routeur n'est pas disponible
    return {
        "selected_model": service.model_names[0] if service.model_names else None,
        "context": {
            "league": league,
            "game_mode": game_mode,
            "game_version": game_version,
        },
        "available_models": service.model_names,
        "note": "Model router not available, using default",
    }


@router.get("/recommendations")
def get_model_recommendations(request: Request) -> Dict[str, Any]:
    """
    Retourne des recommandations de modèles basées sur les patterns d'utilisation.
    SOLITAIRE HACK: Analyse des métadonnées pour suggérer les meilleurs modèles.
    """
    service = request.app.state.prediction_service
    
    recommendations = {
        "most_recent": None,
        "most_specific": None,
        "generic_fallback": None,
        "all_models": service.model_names,
    }
    
    if hasattr(service._fusion_engine, '_model_router'):
        router = service._fusion_engine._model_router
        
        # Trouver le modèle le plus récent (par version de jeu)
        contexts = router.get_available_contexts()
        if contexts["game_versions"]:
            latest_version = contexts["game_versions"][-1]  # Dernière version
            recommendations["latest_game_version"] = latest_version
        
        # Modèle générique de fallback
        recommendations["generic_fallback"] = router.select_model_for_context()
    
    return recommendations
