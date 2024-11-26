import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings
import functools
import inspect

# 创建日志目录
log_path = Path("logs")
log_path.mkdir(exist_ok=True)

# 日志文件路径
error_log = log_path / "error.log"
info_log = log_path / "info.log"

# 移除默认处理器
logger.remove()

# 添加控制台处理器（开发环境）
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 添加错误日志文件处理器
logger.add(
    error_log,
    rotation="500 MB",
    retention="1 week",
    compression="zip",
    level="ERROR",
    encoding="utf-8"
)

# 添加信息日志文件处理器
logger.add(
    info_log,
    rotation="500 MB",
    retention="1 week",
    compression="zip",
    level="INFO",
    encoding="utf-8"
)

def catch_exceptions(func):
    """异常处理装饰器，支持同步和异步函数"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            # 获取函数的参数信息
            sig = inspect.signature(func)
            # 过滤掉多余的参数
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            return await func(*bound_args.args, **bound_args.kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            # 获取函数的参数信息
            sig = inspect.signature(func)
            # 过滤掉多余的参数
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            return func(*bound_args.args, **bound_args.kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise

    # 根据函数类型返回相应的包装器
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
