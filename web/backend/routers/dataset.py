"""Dataset generation and browsing endpoints."""
import asyncio
import json
import os

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect

from web.backend.models.dataset_models import DatasetGenerateRequest, TaskStatus
from web.backend.services import dataset_service

router = APIRouter()


@router.post("/generate")
async def generate_dataset(
    request: DatasetGenerateRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    task_id = dataset_service.create_task(request.num_graphs)
    background_tasks.add_task(dataset_service.run_generation, task_id, request)
    return {"task_id": task_id}


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str) -> TaskStatus:
    status = dataset_service.get_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return status


@router.websocket("/ws/{task_id}")
async def dataset_progress_ws(websocket: WebSocket, task_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            status = dataset_service.get_status(task_id)
            if status is None:
                await websocket.send_json({"error": "task not found"})
                break
            await websocket.send_json(status.model_dump())
            if status.status in ("completed", "failed"):
                break
            await asyncio.sleep(0.4)
    except WebSocketDisconnect:
        pass


@router.get("/{output_dir_b64}/graphs")
async def list_graphs(output_dir_b64: str) -> list:
    """List graph records from a dataset's metadata.json.

    ``output_dir_b64`` is the output_dir path base64-encoded to avoid path
    separator issues in the URL.
    """
    import base64

    try:
        output_dir = base64.urlsafe_b64decode(output_dir_b64 + "==").decode()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid output_dir encoding.")

    meta_path = os.path.join(output_dir, "metadata.json")
    if not os.path.isfile(meta_path):
        raise HTTPException(status_code=404, detail="Dataset metadata not found.")

    with open(meta_path) as f:
        return json.load(f)
