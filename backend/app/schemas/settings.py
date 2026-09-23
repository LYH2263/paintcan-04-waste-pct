from pydantic import BaseModel
class SettingsUpdate(BaseModel):
    coverage: float | None = None
    coats: float | None = None
    waste_pct: float | None = None
    waste_max_pct: float | None = None
