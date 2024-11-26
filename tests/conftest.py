import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from app.core.deps import get_db
from app.crud import crud_user
from app.schemas.user import UserCreate

# 使用MySQL数据库进行测试
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://maxzs:zs1024@127.0.0.1:3306/news_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    """每个测试用例使用独立的数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    """创建测试客户端"""
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def normal_user(client: TestClient, db):
    """创建一个普通用户用于测试"""
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "username": "testuser"
    }
    user_in = UserCreate(**user_data)
    user = crud_user.create(db, obj_in=user_in)
    return {**user_data, "id": user.id}
