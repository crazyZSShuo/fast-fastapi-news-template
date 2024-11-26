from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, articles, comments, health, dashboard, visits

api_router = APIRouter()

# 注册各模块的路由
api_router.include_router(health.router, tags=["系统"])  # 健康检查不需要前缀
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(articles.router, prefix="/articles", tags=["文章"])
api_router.include_router(comments.router, prefix="/comments", tags=["评论"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(visits.router, prefix="/visits", tags=["访问记录相关"])
