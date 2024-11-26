import pytest
from typing import Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.schemas.user import UserCreate

@pytest.fixture
def admin_user(db: Session):
    """创建测试用管理员用户"""
    user_data = {
        "email": "admin@example.com",
        "password": "adminpass123",
        "username": "adminuser"
    }
    user_in = UserCreate(**user_data)
    user = crud_user.create(db, obj_in=user_in)
    # 设置为管理员
    user.role = "admin"
    db.commit()
    return {**user_data, "id": user.id}

@pytest.fixture
def normal_user_token_headers(client: TestClient, normal_user) -> Dict[str, str]:
    """获取普通用户的认证头"""
    login_data = {
        "username": normal_user["email"],
        "password": "testpass123"
    }
    r = client.post("/api/v1/auth/login", data=login_data)
    tokens = r.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}

@pytest.fixture
def admin_token_headers(client: TestClient, admin_user) -> Dict[str, str]:
    """获取管理员用户的认证头"""
    login_data = {
        "username": admin_user["email"],
        "password": "adminpass123"
    }
    r = client.post("/api/v1/auth/login", data=login_data)
    tokens = r.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
