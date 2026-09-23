import pytest
from app.engines.estimate import estimate_room
from app.engines.paint_volume import paint_liters
from app.engines.wall_area import wall_area
from app.modules.waste_pct import WasteError, apply_waste

OPENINGS = [{"w": 0.9, "h": 2.1}, {"w": 1.5, "h": 1.4}]

def test_living_room_net():
    a = wall_area(5, 4, 2.8, OPENINGS)
    assert a["gross_m2"] == 50.4
    assert a["net_m2"] == 46.41

def test_liters_two_coats():
    v = paint_liters(46.41, 8, 2)
    assert v["liters"] == 11.6

def test_estimate_combined():
    e = estimate_room(5, 4, 2.8, OPENINGS, 8, 2)
    assert e["liters"] == 11.6

def test_bad_coverage():
    with pytest.raises(ValueError):
        paint_liters(10, 0, 2)

# ---- 损耗加成 ----

def test_zero_waste_matches_pre_change():
    """缺省 0 损耗时应付升数与改造前同房同参的基础升数一致。"""
    before = paint_liters(46.41, 8, 2)["liters"]
    e = estimate_room(5, 4, 2.8, OPENINGS, 8, 2, 0.0, 20.0)
    assert e["liters"] == before
    assert e["waste_pct"] == 0.0
    assert e["chargeable_liters"] == before

def test_waste_markup():
    w = apply_waste(11.6, 10.0, 20.0)
    assert w["liters"] == 11.6
    assert w["waste_pct"] == 10.0
    assert w["chargeable_liters"] == 12.76

def test_estimate_with_waste():
    e = estimate_room(5, 4, 2.8, OPENINGS, 8, 2, 10.0, 20.0)
    assert e["liters"] == 11.6
    assert e["chargeable_liters"] == 12.76

def test_negative_waste_rejected():
    with pytest.raises(WasteError):
        apply_waste(10.0, -1.0, 20.0)
    with pytest.raises(WasteError):
        estimate_room(5, 4, 2.8, OPENINGS, 8, 2, -0.1, 20.0)

def test_over_cap_waste_rejected():
    with pytest.raises(WasteError):
        apply_waste(10.0, 20.1, 20.0)
    with pytest.raises(WasteError):
        estimate_room(5, 4, 2.8, OPENINGS, 8, 2, 25.0, 20.0)

def test_cap_boundary_allowed():
    w = apply_waste(10.0, 20.0, 20.0)
    assert w["chargeable_liters"] == 12.0
