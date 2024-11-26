from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, get_current_admin_user
from app.crud import crud_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.response import ResponseSchema
from app.core.response import success_response, error_response

router = APIRouter()

@router.get("/me", response_model=ResponseSchema[UserSchema], summary="获取当前用户信息")
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前登录用户信息
    """
    return ResponseSchema(data=current_user)

@router.put("/me", response_model=ResponseSchema[UserSchema], summary="更新当前用户信息")
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新当前登录用户信息
    """
    user = crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
    return ResponseSchema(data=user)

@router.get("", response_model=ResponseSchema[List[UserSchema]], summary="获取用户列表")
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    获取用户列表（仅管理员）
    """
    users = crud_user.user.get_multi(db, skip=skip, limit=limit)
    return ResponseSchema(data=users)

@router.get("/{user_id}", response_model=ResponseSchema[UserSchema], summary="获取指定用户信息")
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    通过ID获取用户信息
    """
    user = crud_user.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )
    if not crud_user.user.is_admin(current_user) and user.id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="无权限访问其他用户信息",
        )
    return ResponseSchema(data=user)
