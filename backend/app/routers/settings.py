from fastapi import APIRouter, HTTPException
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/settings")
def settings():
    with PaintService() as s: return s.settings()
@router.put("/settings")
def put_settings(body: dict[str, str]):
    with PaintService() as s:
        try:
            return s.update_settings(body)
        except ValueError as e:
            raise HTTPException(400, detail=str(e))
