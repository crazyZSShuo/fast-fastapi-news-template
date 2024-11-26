from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VisitBase(BaseModel):
    ip: str
    location: Optional[str] = None
    user_agent: Optional[str] = None
    path: str

class VisitCreate(VisitBase):
    pass

class VisitUpdate(VisitBase):
    pass

class Visit(VisitBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class VisitStats(BaseModel):
    total_visits: int
    visits_by_location: dict
    visits_by_path: dict
    visits_trend: list  # 最近7天的访问趋势
