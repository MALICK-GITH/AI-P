from __future__ import annotations

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.model_loader import preload_model_registry
from app.routers.models import router as models_router
from app.routers.predict import router as predict_router
from app.routers.status import router as status_router
from app.routers.model_context import router as model_context_router
from app.services.prediction_service import PredictionService

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"  # Répertoire models dans app/
PROJECT_ROOT = BASE_DIR.parent
INTEGRATION_MANIFEST_PATH = PROJECT_ROOT / "platform_integration.json"

# SOLITAIRE HACK: Configuration de logging améliorée
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('one_delux_ai.log')
    ]
)
logger = logging.getLogger("one_delux_ai_3")


app = FastAPI(
    title="ONE DELUX AI 3.0",
    version="3.0.0",
    description="Modular FastAPI REST service for live football predictions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status_router)
app.include_router(models_router)
app.include_router(predict_router)
app.include_router(model_context_router)


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "ok",
            "name": "ONE DELUX AI 3.0",
            "version": "3.0.0",
            "description": "Advanced football prediction system with intelligent model routing and caching",
            "features": [
                "16 ML models loaded",
                "Intelligent model routing",
                "Prediction caching for performance",
                "Multi-context predictions",
                "Real-time feature adaptation"
            ],
            "endpoints": {
                "docs": "/docs",
                "openapi": "/openapi.json",
                "health": "/api/status",
                "performance": "/api/performance",
                "models": "/api/models",
                "predict": "/api/predict",
                "model_contexts": "/api/models/contexts",
                "model_selection": "/api/models/select",
                "model_recommendations": "/api/models/recommendations",
                "cache_management": "/api/cache/clear",
                "integration_manifest": "/platform_integration.json",
            },
            "performance": {
                "cache_enabled": True,
                "max_cache_size": 1000,
                "cache_ttl_seconds": 300
            },
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.get("/health")
def health() -> JSONResponse:
    service = app.state.prediction_service
    return JSONResponse(content={"status": "ok", "models_loaded": service.models_loaded})


@app.get("/platform_integration.json")
def platform_integration_manifest() -> JSONResponse:
    if INTEGRATION_MANIFEST_PATH.exists():
        return JSONResponse(content=json.loads(INTEGRATION_MANIFEST_PATH.read_text(encoding="utf-8")))
    return JSONResponse(
        content={
            "detail": "Integration manifest not found",
            "path": str(INTEGRATION_MANIFEST_PATH),
        },
        status_code=404,
    )


@app.on_event("startup")
def startup_event() -> None:
    # SOLITAIRE HACK: Utiliser le chemin relatif depuis le répertoire courant
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_path = os.path.join(current_dir, "models")
    
    registry = preload_model_registry(models_path)
    app.state.model_registry = registry
    app.state.prediction_service = PredictionService(registry)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    # SOLITAIRE HACK: Logging détaillé des erreurs de validation
    logger.error(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": {str(index): error["msg"] for index, error in enumerate(exc.errors())},
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    # SOLITAIRE HACK: Logging détaillé des erreurs de validation de requête
    logger.error(f"Request validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation error",
            "errors": {str(index): error["msg"] for index, error in enumerate(exc.errors())},
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # SOLITAIRE HACK: Logging détaillé des erreurs génériques avec contexte
    logger.exception(f"Unhandled error on {request.url}: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
            "timestamp": datetime.now().isoformat(),
        }
    )
