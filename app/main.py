from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.model_loader import preload_model_registry
from app.routers.models import router as models_router
from app.routers.predict import router as predict_router
from app.routers.status import router as status_router
from app.services.prediction_service import PredictionService

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
PROJECT_ROOT = BASE_DIR.parent
INTEGRATION_MANIFEST_PATH = PROJECT_ROOT / "platform_integration.json"

logger = logging.getLogger("one_delux_ai_2")


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


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "ok",
            "name": "ONE DELUX AI 3.0",
            "version": "3.0.0",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/api/status",
            "models": "/api/models",
            "predict": "/api/predict",
            "integration_manifest": "/platform_integration.json",
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
    registry = preload_model_registry(str(MODELS_DIR))
    app.state.model_registry = registry
    app.state.prediction_service = PredictionService(registry)


@app.exception_handler(ValidationError)
async def validation_exception_handler(_: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": {str(index): error["msg"] for index, error in enumerate(exc.errors())},
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": {str(index): error["msg"] for index, error in enumerate(exc.errors())},
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
