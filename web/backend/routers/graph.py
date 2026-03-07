"""Graph generation and retrieval endpoints."""
import asyncio
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from web.backend.models.graph_models import (
    GraphGenerateRequest,
    GraphGenerateResponse,
    GraphUploadResponse,
)
from web.backend.services import graph_service, graph_store, serialization, upload_service

router = APIRouter()


@router.post("/generate", response_model=GraphGenerateResponse)
async def generate_graph(request: GraphGenerateRequest) -> GraphGenerateResponse:
    try:
        graph_id, elements, stats = await asyncio.to_thread(graph_service.generate, request)
        return GraphGenerateResponse(graph_id=graph_id, elements=elements, stats=stats)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/upload", response_model=GraphUploadResponse)
async def upload_graph(files: List[UploadFile] = File(...)) -> GraphUploadResponse:
    try:
        graph_id, elements, stats, file_count, folder_path, warnings = (
            await asyncio.to_thread(upload_service.upload, files)
        )
        return GraphUploadResponse(
            graph_id=graph_id,
            elements=elements,
            stats=stats,
            file_count=file_count,
            folder_path=folder_path,
            warnings=warnings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{graph_id}")
async def get_graph(graph_id: str) -> dict:
    try:
        graph = graph_store.get(graph_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    elements = serialization.graph_to_elements(graph)
    return {"graph_id": graph_id, "elements": [e.model_dump() for e in elements]}
