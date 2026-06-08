from __future__ import annotations

from fastapi import APIRouter, Request

from app.schemas.response_schema import ModelsResponse

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=ModelsResponse)
def list_models(request: Request) -> ModelsResponse:
    service = request.app.state.prediction_service
    return ModelsResponse(models=service.model_metadata())
