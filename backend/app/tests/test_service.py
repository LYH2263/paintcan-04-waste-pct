import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="paintcan-test-")
os.environ["DATA_DIR"] = _tmp

from app.db import connect  # noqa: E402
from app import seed  # noqa: E402
from app.services.paint_service import PaintService  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _seeded():
    seed.init_db()
    yield


def _run_count():
    with connect() as c:
        return c.execute("SELECT COUNT(*) n FROM calc_runs").fetchone()["n"]


def test_persist_pins_waste_and_chargeable():
    with PaintService() as s:
        r = s.estimate(1, True, waste_pct=10.0)
    rid = r["run_id"]
    assert rid is not None
    assert r["liters"] == 11.6
    assert r["waste_pct"] == 10.0
    assert r["chargeable_liters"] == 12.76
    with PaintService() as s:
        got = s.run_by_id(rid)
    assert got["liters"] == 11.6
    assert got["waste_pct"] == 10.0
    assert got["chargeable_liters"] == 12.76


def test_changing_default_does_not_move_old_rows():
    with PaintService() as s:
        rid = s.estimate(1, True, waste_pct=5.0)["run_id"]
        before = s.run_by_id(rid)
        # 之后把默认损耗与上限调高
        s.update_settings({"waste_pct": 15.0, "waste_max_pct": 30.0})
        after = s.run_by_id(rid)
    assert before["chargeable_liters"] == after["chargeable_liters"] == round(11.6 * 1.05, 2)
    assert after["waste_pct"] == 5.0


def test_negative_waste_rejected_and_not_written():
    before = _run_count()
    with PaintService() as s:
        with pytest.raises(ValueError):
            s.estimate(1, True, waste_pct=-1.0)
    assert _run_count() == before


def test_over_cap_waste_rejected_and_not_written():
    before = _run_count()
    with PaintService() as s:
        with pytest.raises(ValueError):
            s.estimate(1, True, waste_pct=999.0)
    assert _run_count() == before


def test_persist_false_returns_but_does_not_write():
    before = _run_count()
    with PaintService() as s:
        r = s.estimate(1, False, waste_pct=10.0)
    assert r["run_id"] is None
    assert r["chargeable_liters"] == 12.76
    assert _run_count() == before


def test_default_waste_zero_chargeable_equals_base():
    with PaintService() as s:
        s.update_settings({"waste_pct": 0.0, "waste_max_pct": 20.0})
        r = s.estimate(1, False)
    assert r["waste_pct"] == 0.0
    assert r["chargeable_liters"] == r["liters"]
