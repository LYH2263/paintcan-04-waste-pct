from fastapi import APIRouter, HTTPException
from app.schemas.estimate import EstimateRequest
from app.services.paint_service import PaintService
router = APIRouter()
@router.post("/estimate")
def post_estimate(body: EstimateRequest):
    with PaintService() as s:
        try:
            r = s.estimate(body.room_id, body.persist, body.coats, body.coverage, body.waste_pct)
        except ValueError as e:
            # 损耗为负/超上限或参数非法：整单拒绝，服务层尚未写入任何记录
            raise HTTPException(400, str(e))
        if not r: raise HTTPException(404)
        return r
