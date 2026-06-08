from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas.request_schema import PredictionRequest
from app.schemas.response_schema import PredictionResponse

router = APIRouter(prefix="/api/predict", tags=["predict"])


def _build_response(payload: dict) -> PredictionResponse:
    return PredictionResponse(**payload)


@router.post("", response_model=PredictionResponse)
def predict(request: Request, body: PredictionRequest) -> PredictionResponse:
    service = request.app.state.prediction_service
    try:
        return _build_response(service.predict_fusion(body))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Model not available: {exc.args[0]}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive wrapper
        raise HTTPException(status_code=500, detail="Internal prediction error") from exc


@router.post("/over-under", response_model=dict)
def predict_over_under(request: Request, body: PredictionRequest) -> dict:
    service = request.app.state.prediction_service
    try:
        features = service.build_feature_vector(body)
        return service.predict_over_under(body, features)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/home-goals", response_model=dict)
def predict_home_goals(request: Request, body: PredictionRequest) -> dict:
    service = request.app.state.prediction_service
    try:
        features = service.build_feature_vector(body)
        return service.predict_home_goals(body, features)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/away-goals", response_model=dict)
def predict_away_goals(request: Request, body: PredictionRequest) -> dict:
    service = request.app.state.prediction_service
    try:
        features = service.build_feature_vector(body)
        return service.predict_away_goals(body, features)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/total-goals", response_model=dict)
def predict_total_goals(request: Request, body: PredictionRequest) -> dict:
    service = request.app.state.prediction_service
    try:
        features = service.build_feature_vector(body)
        return service.predict_total_goals(body, features)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/fusion", response_model=dict)
def predict_fusion(request: Request, body: PredictionRequest) -> dict:
    service = request.app.state.prediction_service
    try:
        return service.predict_fusion(body)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        raise HTTPException(status_code=400, detail=str(exc)) from exc
