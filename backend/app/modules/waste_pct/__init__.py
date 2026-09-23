"""损耗加成：在净面积换算出的基础升数上，按损耗百分点加成得到应付升数。

应付升数 = 基础升数 × (1 + 损耗百分点 / 100)
损耗不允许为负，且不得超过设置的上限，否则整单拒绝。
"""


class WasteError(ValueError):
    """损耗百分点为负或超过上限。"""


def apply_waste(base_liters: float, waste_pct: float, max_pct: float | None = None) -> dict:
    pct = float(waste_pct)
    if pct < 0:
        raise WasteError("waste_pct must not be negative")
    if max_pct is not None and pct > float(max_pct):
        raise WasteError(f"waste_pct {pct} exceeds max {max_pct}")
    base = round(float(base_liters), 2)
    chargeable = round(base * (1.0 + pct / 100.0), 2)
    return {"liters": base, "waste_pct": pct, "chargeable_liters": chargeable}
