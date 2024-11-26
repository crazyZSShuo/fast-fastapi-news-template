from typing import List
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    # 项目基本设置
    PROJECT_NAME: str
    API_V1_STR: str
    
    # 数据库设置
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: str
    MYSQL_DATABASE: str
    
    # Redis设置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = None
    
    # JWT设置
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    
    # CORS设置
    CORS_ORIGINS: List[str]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 缓存设置
    DEFAULT_CACHE_EXPIRE: int = 3600  # 默认缓存过期时间（秒）
    
    # 监控设置
    ENABLE_PERFORMANCE_MONITORING: bool = True
    MONITORING_INTERVAL: int = 60  # 性能数据收集间隔（秒）
    
    # API文档设置
    API_TITLE: str = "News API"
    API_DESCRIPTION: str = """
    新闻管理系统API接口文档。
    提供新闻的增删改查、用户管理、权限控制等功能。
    """
    API_VERSION: str = "1.0.0"
    API_TERMS_OF_SERVICE: str = "http://example.com/terms/"
    API_CONTACT: dict = {
        "name": "API Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com"
    }
    API_LICENSE: dict = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    }
    
    # 其他设置
    ITEMS_PER_PAGE: int = 10

    class Config:
        case_sensitive = True
        env_file = ".env"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "CORS_ORIGINS":
                return json.loads(raw_val)
            return raw_val

settings = Settings()
