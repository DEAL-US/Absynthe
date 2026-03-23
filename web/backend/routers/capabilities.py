"""Capability endpoints exposing modular components and parameter schemas."""
from fastapi import APIRouter

from web.backend.services.registry import (
    COMPOSITION_SCHEMAS,
    DISTRIBUTION_SCHEMAS,
    LABELING_FUNCTION_SCHEMAS,
    MOTIF_SCHEMAS,
    PERTURBATION_SCHEMAS,
    STRATEGY_SCHEMAS,
)

router = APIRouter()


@router.get("/motifs")
async def get_motifs() -> list:
    return MOTIF_SCHEMAS


@router.get("/compositions")
async def get_compositions() -> list:
    return COMPOSITION_SCHEMAS


@router.get("/strategies")
async def get_strategies() -> list:
    return STRATEGY_SCHEMAS


@router.get("/labeling-functions")
async def get_labeling_functions() -> list:
    return LABELING_FUNCTION_SCHEMAS


@router.get("/perturbations")
async def get_perturbations() -> list:
    return PERTURBATION_SCHEMAS


@router.get("/distributions")
async def get_distributions() -> list:
    return DISTRIBUTION_SCHEMAS
