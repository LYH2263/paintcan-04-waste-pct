"""waste_pct 损耗加成模块。

在净面积换算出的基础升数之上，按损耗百分比加成得到应付升数：
payable = base * (1 + pct / 100)。损耗为负或超过上限时抛 WastePctError，
调用方须整单拒绝且不得写入任何记录。
"""

DEFAULT_WASTE_PCT = 0.0
DEFAULT_MAX_WASTE_PCT = 20.0


class WastePctError(ValueError):
    """损耗百分比非法：为负或超过上限。"""


def check_waste_pct(waste_pct, max_pct=DEFAULT_MAX_WASTE_PCT):
    """校验损耗百分点，合法则返回归一化后的浮点值。"""
    pct = float(waste_pct)
    cap = float(max_pct)
    if pct < 0:
        raise WastePctError(f"waste pct must be >= 0, got {pct}")
    if pct > cap:
        raise WastePctError(f"waste pct {pct} exceeds max {cap}")
    return pct


def apply_waste(base_liters, waste_pct=DEFAULT_WASTE_PCT, max_pct=DEFAULT_MAX_WASTE_PCT):
    """基础升数按损耗加成，返回钉选用的三元组。

    损耗为 0 时 payable_liters 与 base_liters 完全一致。
    """
    pct = check_waste_pct(waste_pct, max_pct)
    base = round(float(base_liters), 2)
    return {
        "base_liters": base,
        "waste_pct": pct,
        "payable_liters": round(base * (1 + pct / 100.0), 2),
    }
