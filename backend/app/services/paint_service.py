import json
from app.db import connect
from app.engines.estimate import estimate_room
from app.modules import waste_pct as waste_mod
from app.repositories import openings, rooms, runs, settings

class PaintService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_rooms(self): return rooms.list_all(self._c)
    def room_detail(self, rid):
        r = rooms.get(self._c, rid)
        if not r: return None
        return {"room": r, "openings": openings.for_room(self._c, rid)}
    def settings(self): return settings.get_map(self._c)
    def update_settings(self, values):
        merged = {**settings.get_map(self._c), **{k: str(v) for k, v in values.items()}}
        pct = float(merged.get("waste_pct", "0"))
        cap = float(merged.get("waste_max_pct", "20"))
        if pct < 0 or cap < 0:
            raise ValueError("waste_pct and waste_max_pct must be >= 0")
        if pct > cap:
            raise ValueError(f"waste_pct {pct} exceeds waste_max_pct {cap}")
        settings.set_values(self._c, values)
        return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def history_detail(self, run_id):
        r = runs.get(self._c, run_id)
        if not r: return None
        return {**r, "input": json.loads(r["input_json"]), "result": json.loads(r["result_json"])}
    def estimate(self, room_id, persist, coats=None, coverage=None, waste_pct=None):
        detail = self.room_detail(room_id)
        if not detail: return None
        r = detail["room"]
        cov, ct = settings.coverage_coats(self._c)
        cov = float(coverage or cov)
        ct = int(coats or ct)
        dft_pct, max_pct = settings.waste_defaults(self._c)
        pct = dft_pct if waste_pct is None else float(waste_pct)
        ops = [{"w": o["w"], "h": o["h"]} for o in detail["openings"]]
        result = estimate_room(r["length"], r["width"], r["height"], ops, cov, ct)
        # 损耗非法（为负或超上限）时在此抛出，先于任何写库 → 整单拒绝且无记录
        result = {**result, **waste_mod.apply_waste(result["liters"], pct, max_pct)}
        rid = runs.insert(self._c, "estimate",
            {"room_id": room_id, "coats": ct, "coverage": cov, "waste_pct": pct}, result, room_id) if persist else None
        return {"run_id": rid, "room_id": room_id, **result}
    def dashboard(self):
        rs = rooms.list_all(self._c)
        return {"room_count": len(rs), "clean": len([x for x in rs if "种子" not in x["name"] and "多种" not in x["name"]]), "dirty": len([x for x in rs if "多种" in x["name"]])}
