from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 项目基本设置
    PROJECT_NAME: str = "News API"
    API_V1_STR: str = "/api/v1"
    
    # 数据库设置
    MYSQL_USER: str = "maxzs"
    MYSQL_PASSWORD: str = "zs1024"
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: str = "3306"
    MYSQL_DATABASE: str = "news_db"
    
    # JWT设置
    SECRET_KEY: str = "your-secret-key-here"  # 请在生产环境中更改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # 其他设置
    ITEMS_PER_PAGE: int = 10

    class Config:
        case_sensitive = True

settings = Settings()
