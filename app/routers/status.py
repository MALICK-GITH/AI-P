from __future__ import annotations

from fastapi import APIRouter, Request
from typing import Dict, Any

from app.schemas.response_schema import StatusResponse

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status", response_model=StatusResponse)
def status(request: Request) -> StatusResponse:
    service = request.app.state.prediction_service
    return StatusResponse(status="ok", models_loaded=service.models_loaded)


@router.get("/performance")
def performance_stats(request: Request) -> Dict[str, Any]:
    """
    SOLITAIRE HACK: Retourne les statistiques de performance du système.
    Inclut les statistiques du cache de prédictions pour optimiser les performances.
    """
    service = request.app.state.prediction_service
    
    stats = {
        "models_loaded": service.models_loaded,
        "model_names": service.model_names,
        "cache_stats": None,
    }
    
    # Ajouter les statistiques du cache si disponibles
    if hasattr(service._fusion_engine, 'get_cache_stats'):
        stats["cache_stats"] = service._fusion_engine.get_cache_stats()
    
    return stats


@router.post("/cache/clear")
def clear_cache(request: Request) -> Dict[str, str]:
    """
    SOLITAIRE HACK: Vide le cache de prédictions.
    Force un recalcul pour les prochaines requêtes.
    """
    service = request.app.state.prediction_service
    
    if hasattr(service._fusion_engine, 'clear_cache'):
        service._fusion_engine.clear_cache()
        return {"status": "success", "message": "Prediction cache cleared"}
    
    return {"status": "error", "message": "Cache not available"}

