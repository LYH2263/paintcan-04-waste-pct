from app.engines.paint_volume import paint_liters
from app.engines.wall_area import wall_area
from app.modules.waste_pct import apply_waste

def estimate_room(length, width, height, openings, coverage, coats, waste_pct=0.0, max_waste_pct=None):
    area = wall_area(length, width, height, openings)
    vol = paint_liters(area["net_m2"], coverage, coats)
    waste = apply_waste(vol["liters"], waste_pct, max_waste_pct)
    # liters/waste_pct/chargeable_liters 来自损耗模块；coats/coverage 沿用基础换算
    return {**area, **vol, **waste}
