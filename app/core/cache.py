from typing import Any, Optional
from redis import Redis
from app.core.config import settings
from app.core.logger import logger
import json
import pickle
from datetime import timedelta
from functools import wraps

class RedisCache:
    def __init__(self):
        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None
        )
        self._test_connection()

    def _test_connection(self):
        try:
            self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {str(e)}")

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存值"""
        try:
            if isinstance(value, (dict, list, str, int, float, bool)):
                value = json.dumps(value)
            else:
                value = pickle.dumps(value)
            return self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            return False

    def update(self, key: str, value: Any, expire: int = 3600) -> bool:
        """更新缓存"""
        try:
            # 先删除旧缓存
            self.delete(key)
            # 设置新缓存
            return self.set(key, value, expire)
        except Exception as e:
            logger.error(f"Error updating cache key {key}: {str(e)}")
            return False

    def delete_pattern(self, pattern: str) -> bool:
        """删除匹配模式的所有缓存"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {str(e)}")
            return False

    def clear_all(self) -> bool:
        """清除所有缓存"""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

    def get_or_set(self, key: str, value_func, expire: int = 3600) -> Any:
        """获取缓存，如果不存在则设置"""
        value = self.get(key)
        if value is None:
            value = value_func()
            self.set(key, value, expire)
        return value

# 缓存装饰器
def cache(expire: int = 3600, key_prefix: str = ""):
    """缓存装饰器
    :param expire: 过期时间（秒）
    :param key_prefix: 键前缀
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:"
            if args:
                cache_key += ":".join(str(arg) for arg in args)
            if kwargs:
                cache_key += ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

            # 尝试从缓存获取
            cached_value = redis_cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value

            # 执行原函数
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            
            # 存储结果到缓存
            if result is not None:
                redis_cache.set(cache_key, result, expire)
                logger.debug(f"Cached result for key: {cache_key}")
            
            return result
            
        return wrapper
    return decorator

# 创建全局缓存实例
redis_cache = RedisCache()
