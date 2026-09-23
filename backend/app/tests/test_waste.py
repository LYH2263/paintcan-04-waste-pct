import os
import tempfile

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="paintcan-test-"))

import pytest

from app import seed
from app.modules import waste_pct
from app.modules.waste_pct import WastePctError
from app.services.paint_service import PaintService


def setup_module():
    seed.init_db()


# ---- 模块层 ----

def test_waste_zero_matches_base():
    w = waste_pct.apply_waste(11.6, 0)
    assert w == {"base_liters": 11.6, "waste_pct": 0.0, "payable_liters": 11.6}

def test_waste_surcharge():
    w = waste_pct.apply_waste(11.6, 10)
    assert w["payable_liters"] == 12.76
    assert w["base_liters"] == 11.6
    assert w["waste_pct"] == 10.0

def test_waste_negative_rejected():
    with pytest.raises(WastePctError):
        waste_pct.apply_waste(11.6, -1)

def test_waste_over_max_rejected():
    with pytest.raises(WastePctError):
        waste_pct.apply_waste(11.6, 21, 20)
    assert waste_pct.apply_waste(11.6, 20, 20)["payable_liters"] == 13.92


# ---- 服务层 ----

def test_estimate_default_waste_zero_parity():
    with PaintService() as s:
        r = s.estimate(1, False)
    assert r["waste_pct"] == 0.0
    assert r["base_liters"] == 11.6
    assert r["payable_liters"] == 11.6  # 与改造前同房同参一致
    assert r["liters"] == 11.6

def test_estimate_with_waste():
    with PaintService() as s:
        r = s.estimate(1, False, waste_pct=10)
    assert (r["base_liters"], r["waste_pct"], r["payable_liters"]) == (11.6, 10.0, 12.76)

def test_no_persist_writes_nothing():
    with PaintService() as s:
        before = len(s.history(100))
        r = s.estimate(1, False, waste_pct=5)
        assert r["run_id"] is None
        assert len(s.history(100)) == before

def test_persist_pins_waste_triple():
    with PaintService() as s:
        r = s.estimate(1, True, waste_pct=10)
        h = s.history_detail(r["run_id"])
    assert h["result"]["base_liters"] == 11.6
    assert h["result"]["waste_pct"] == 10.0
    assert h["result"]["payable_liters"] == 12.76
    assert h["input"]["waste_pct"] == 10.0

def test_invalid_waste_rejects_whole_order():
    with PaintService() as s:
        before = len(s.history(100))
        for bad in (-1, 21):
            with pytest.raises(WastePctError):
                s.estimate(1, True, waste_pct=bad)
        assert len(s.history(100)) == before  # 整单拒绝，不写记录

def test_history_detail_unknown_id():
    with PaintService() as s:
        assert s.history_detail(999999) is None

def test_default_waste_change_keeps_old_runs():
    with PaintService() as s:
        old = s.estimate(1, True)  # 默认损耗 0 → 应付 11.6
        s.update_settings({"waste_pct": "5"})
        new = s.estimate(1, False)  # 新默认 5%
        assert new["waste_pct"] == 5.0
        assert new["payable_liters"] == 12.18
        again = s.history_detail(old["run_id"])
        assert again["result"]["payable_liters"] == 11.6  # 旧条不跟着变
        assert again["result"]["waste_pct"] == 0.0
        s.update_settings({"waste_pct": "0"})  # 还原，避免影响其他用例

def test_update_settings_validation():
    with PaintService() as s:
        with pytest.raises(ValueError):
            s.update_settings({"waste_pct": "-1"})
        with pytest.raises(ValueError):
            s.update_settings({"waste_pct": "30"})  # 超过上限 20
        with pytest.raises(ValueError):
            s.update_settings({"waste_max_pct": "-5"})
