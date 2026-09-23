from fastapi import APIRouter, HTTPException
from app.schemas.settings import SettingsUpdate
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/settings")
def settings():
    with PaintService() as s: return s.settings()
@router.put("/settings")
def update_settings(body: SettingsUpdate):
    with PaintService() as s:
        try:
            return s.update_settings(body.model_dump(exclude_none=True))
        except ValueError as e:
            raise HTTPException(400, str(e))
