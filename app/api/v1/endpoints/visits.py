from typing import Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_admin_user
from app.crud import crud_visit
from app.schemas.visit import VisitCreate, Visit, VisitStats
from app.schemas.response import ResponseSchema
from app.models.user import User

router = APIRouter()

@router.post("", response_model=ResponseSchema[Visit], summary="记录访问")
def create_visit(
    *,
    db: Session = Depends(get_db),
    request: Request,
) -> Any:
    """
    记录访问信息
    """
    client_host = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent", "Unknown")
    path = str(request.url.path)

    visit_in = VisitCreate(
        ip=client_host,
        user_agent=user_agent,
        path=path
    )
    visit = crud_visit.visit.create_with_location(db=db, obj_in=visit_in)
    return ResponseSchema(data=visit)

@router.get("/stats", response_model=ResponseSchema[VisitStats], summary="获取访问统计")
def get_visit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    获取访问统计信息（仅管理员）
    """
    stats = crud_visit.visit.get_visit_stats(db=db)
    return ResponseSchema(data=stats)
