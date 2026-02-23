"""Perturbation endpoints."""
import asyncio

from fastapi import APIRouter, HTTPException

from web.backend.models.perturbation_models import PerturbationRequest, PerturbationResponse
from web.backend.services import perturbation_service

router = APIRouter()


@router.post("/apply", response_model=PerturbationResponse)
async def apply_perturbation(request: PerturbationRequest) -> PerturbationResponse:
    try:
        return await asyncio.to_thread(perturbation_service.apply, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
