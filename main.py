from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logger import logger, catch_exceptions
from app.core.monitoring import monitor, log_request_performance
from app.core.cache import redis_cache
from app.api.v1.api import api_router
from app.db.session import engine, Base, check_database_connection
import uvicorn
import time
from app.core.cache import cache

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建限速器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info("Starting up application...")
    # 检查数据库连接
    if await check_database_connection():
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed")
    
    yield  # 应用运行
    
    # 关闭事件
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    terms_of_service=settings.API_TERMS_OF_SERVICE,
    contact=settings.API_CONTACT,
    license_info=settings.API_LICENSE,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 添加可信主机中间件
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# 添加限速中间件
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 添加请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录请求性能
        await log_request_performance(request, process_time)
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        await log_request_performance(request, process_time, is_error=True)
        raise

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": f"Internal Server Error: {str(exc)}",
            "data": None
        }
    )

# 监控端点
@app.get("/metrics")
@catch_exceptions
@cache(expire=60, key_prefix="metrics")  # 缓存1分钟
async def get_metrics():
    """获取应用性能指标"""
    if not settings.ENABLE_PERFORMANCE_MONITORING:
        return {"message": "Performance monitoring is disabled"}
    return monitor.get_all_stats()

# 健康检查端点
@app.get("/health")
@catch_exceptions
@cache(expire=30, key_prefix="health")  # 缓存30秒
async def health_check():
    """系统健康检查"""
    db_status = await check_database_connection()
    cache_status = redis_cache.redis_client.ping()
    
    return {
        "status": "healthy" if db_status and cache_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "cache": "connected" if cache_status else "disconnected",
        "timestamp": time.time()
    }

# 根路由
@app.get("/")
@catch_exceptions
@cache(expire=3600, key_prefix="root")  # 缓存1小时
async def root():
    logger.info("Root endpoint accessed")
    return {
        "code": 200,
        "message": "Welcome to News API",
        "data": {
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "metrics_url": "/metrics",
            "health_url": "/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
