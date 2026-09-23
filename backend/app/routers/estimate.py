from fastapi import APIRouter, HTTPException
from app.modules.waste_pct import WastePctError
from app.schemas.estimate import EstimateRequest
from app.services.paint_service import PaintService
router = APIRouter()
@router.post("/estimate")
def post_estimate(body: EstimateRequest):
    with PaintService() as s:
        try:
            r = s.estimate(body.room_id, body.persist, body.coats, body.coverage, body.waste_pct)
        except WastePctError as e:
            raise HTTPException(400, detail=str(e))
        if not r: raise HTTPException(404)
        return r
