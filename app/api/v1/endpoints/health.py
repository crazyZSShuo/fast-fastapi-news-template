from fastapi import APIRouter
from typing import Dict
import time
from app.core.config import settings
from app.db.session import SessionLocal

router = APIRouter()

@router.get("/health", response_model=Dict)
def health_check():
    """
    健康检查接口
    返回:
        - status: 服务状态 ('healthy' 或 'unhealthy')
        - timestamp: 当前时间戳
        - version: API版本
        - database: 数据库连接状态
    """
    health_data = {
        "status": "healthy",
        "timestamp": int(time.time()),
        "version": "1.0.0",
        "service": settings.PROJECT_NAME,
        "database": "connected"
    }
    
    # 检查数据库连接
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["database"] = "disconnected"
        health_data["error"] = str(e)
    
    return health_data
