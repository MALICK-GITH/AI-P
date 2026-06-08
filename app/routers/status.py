from __future__ import annotations

from fastapi import APIRouter, Request

from app.schemas.response_schema import StatusResponse

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status", response_model=StatusResponse)
def status(request: Request) -> StatusResponse:
    service = request.app.state.prediction_service
    return StatusResponse(status="ok", models_loaded=service.models_loaded)

