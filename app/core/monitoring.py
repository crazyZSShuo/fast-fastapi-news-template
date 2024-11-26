from fastapi import Request
from app.core.logger import logger
import time
import psutil
import platform
from typing import Dict, Any
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
        self.max_response_time = 0
        self.min_response_time = float('inf')

    def record_request(self, response_time: float, is_error: bool = False):
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.total_response_time += response_time
        self.max_response_time = max(self.max_response_time, response_time)
        self.min_response_time = min(self.min_response_time, response_time)

    def get_system_stats(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": cpu_percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_free": disk.free,
                "disk_percent": disk.percent
            }
        }

    def get_application_stats(self) -> Dict[str, Any]:
        uptime = datetime.now() - self.start_time
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "application": {
                "uptime_seconds": uptime.total_seconds(),
                "start_time": self.start_time.isoformat(),
                "total_requests": self.request_count,
                "error_count": self.error_count,
                "average_response_time": avg_response_time,
                "max_response_time": self.max_response_time,
                "min_response_time": self.min_response_time if self.min_response_time != float('inf') else 0,
                "success_rate": (
                    (self.request_count - self.error_count) / self.request_count * 100 
                    if self.request_count > 0 else 100
                )
            }
        }

    def get_process_stats(self) -> Dict[str, Any]:
        process = psutil.Process()
        return {
            "process": {
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections())
            }
        }

    def get_all_stats(self) -> Dict[str, Any]:
        stats = {}
        stats.update(self.get_system_stats())
        stats.update(self.get_application_stats())
        stats.update(self.get_process_stats())
        return stats

# 创建全局监控实例
monitor = PerformanceMonitor()

async def log_request_performance(request: Request, response_time: float, is_error: bool = False):
    """记录请求性能指标"""
    monitor.record_request(response_time, is_error)
    
    # 记录详细的请求信息
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client_host": request.client.host if request.client else None,
        "response_time": f"{response_time:.3f}s",
        "is_error": is_error
    }
    
    if is_error:
        logger.warning(f"Request performance log: {log_data}")
    else:
        logger.info(f"Request performance log: {log_data}")
