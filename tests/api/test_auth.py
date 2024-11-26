import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_register_user(client: TestClient, db: Session):
    """测试用户注册"""
    data = {
        "email": "newuser@example.com",
        "password": "newpass123",
        "username": "newuser"
    }
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["data"]["email"] == data["email"]
    assert content["data"]["username"] == data["username"]
    assert "id" in content["data"]

def test_register_existing_email(client: TestClient, normal_user):
    """测试注册已存在的邮箱"""
    data = {
        "email": normal_user["email"],  # 使用已存在的邮箱
        "password": "anotherpass123",
        "username": "anotheruser"
    }
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 400
    assert "该邮箱已被注册" in response.json()["detail"]

def test_login_success(client: TestClient, normal_user):
    """测试登录成功"""
    login_data = {
        "username": normal_user["email"],
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, normal_user):
    """测试登录密码错误"""
    login_data = {
        "username": normal_user["email"],
        "password": "wrongpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "邮箱或密码错误" in response.json()["detail"]

def test_login_nonexistent_user(client: TestClient):
    """测试登录不存在的用户"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "somepass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "邮箱或密码错误" in response.json()["detail"]

def test_refresh_token(client: TestClient, normal_user):
    """测试刷新token"""
    # 先登录获取refresh token
    login_data = {
        "username": normal_user["email"],
        "password": "testpass123"
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    refresh_token = login_response.json()["refresh_token"]
    
    # 使用refresh token获取新的access token
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

def test_refresh_invalid_token(client: TestClient):
    """测试使用无效的refresh token"""
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})
    assert response.status_code == 401
    assert "无效的refresh token" in response.json()["detail"]
