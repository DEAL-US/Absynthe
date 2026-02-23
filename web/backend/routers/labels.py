"""Label assignment endpoints."""
import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from web.backend.models.graph_models import LabeledGraphResponse, LabelDistribution
from web.backend.services import label_service

router = APIRouter()


class LabelAssignRequest(BaseModel):
    graph_id: str
    motif_order: Optional[list] = None


@router.post("/assign", response_model=LabeledGraphResponse)
async def assign_labels(req: LabelAssignRequest) -> LabeledGraphResponse:
    try:
        graph_id, elements, dist = await asyncio.to_thread(
            label_service.assign, req.graph_id, req.motif_order
        )
        return LabeledGraphResponse(
            graph_id=graph_id,
            elements=elements,
            label_distribution=LabelDistribution(counts=dist),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/reassign", response_model=LabeledGraphResponse)
async def reassign_labels(req: LabelAssignRequest) -> LabeledGraphResponse:
    try:
        graph_id, elements, dist = await asyncio.to_thread(
            label_service.reassign, req.graph_id, req.motif_order
        )
        return LabeledGraphResponse(
            graph_id=graph_id,
            elements=elements,
            label_distribution=LabelDistribution(counts=dist),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
