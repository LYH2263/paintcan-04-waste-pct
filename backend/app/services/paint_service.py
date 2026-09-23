from app.db import connect
from app.engines.estimate import estimate_room
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
    def update_settings(self, values: dict):
        m = settings.get_map(self._c)
        # 先规整类型（coats 必须以整数字符串落库，避免 int("2.0") 解析失败）
        if "coats" in values and values["coats"] is not None:
            values["coats"] = int(float(values["coats"]))
        m.update({k: str(v) for k, v in values.items() if v is not None})
        coverage = float(m.get("coverage", "8"))
        coats = int(float(m.get("coats", "2")))
        waste_pct = float(m.get("waste_pct", "0"))
        waste_max = float(m.get("waste_max_pct", "20"))
        if coverage <= 0:
            raise ValueError("coverage must be positive")
        if coats <= 0:
            raise ValueError("coats must be positive")
        if waste_pct < 0 or waste_max < 0:
            raise ValueError("waste percentages must not be negative")
        if waste_pct > waste_max:
            raise ValueError("default waste_pct must not exceed waste_max_pct")
        for k, v in values.items():
            if v is not None:
                settings.upsert(self._c, k, v)
        return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def run_by_id(self, run_id): return runs.get(self._c, run_id)
    def estimate(self, room_id, persist, coats=None, coverage=None, waste_pct=None):
        detail = self.room_detail(room_id)
        if not detail: return None
        r = detail["room"]
        cov, ct = settings.coverage_coats(self._c)
        cov = float(coverage or cov)
        ct = int(coats or ct)
        default_waste, waste_max = settings.waste_defaults(self._c)
        pct = default_waste if waste_pct is None else float(waste_pct)
        ops = [{"w": o["w"], "h": o["h"]} for o in detail["openings"]]
        # 非法损耗（负/超上限）在此抛出，由路由转 400；在任何写入之前，故不落记录
        result = estimate_room(r["length"], r["width"], r["height"], ops, cov, ct, pct, waste_max)
        payload = {"room_id": room_id, "coats": ct, "coverage": cov, "waste_pct": pct}
        rid = runs.insert(self._c, "estimate", payload, result, room_id) if persist else None
        return {"run_id": rid, "room_id": room_id, **result}
    def dashboard(self):
        rs = rooms.list_all(self._c)
        return {"room_count": len(rs), "clean": len([x for x in rs if "种子" not in x["name"] and "多种" not in x["name"]]), "dirty": len([x for x in rs if "多种" in x["name"]])}
