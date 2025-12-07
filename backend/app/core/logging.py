"""
结构化日志系统

支持：
- JSON 结构化日志（便于 ELK/Splunk 解析）
- 彩色控制台输出（开发环境）
- 日志轮转（按时间/按大小）
- 请求追踪（request_id）
- 访问日志分离
- 性能监控日志
"""
import logging
import sys
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional
from datetime import datetime
from contextvars import ContextVar

from app.core.config import settings, get_log_dir

# 上下文变量：存储当前请求的 request_id
current_request_id: ContextVar[str] = ContextVar("request_id", default="system")


class JSONFormatter(logging.Formatter):
    """
    JSON 格式日志
    
    便于日志聚合系统（ELK、Splunk、CloudWatch）解析
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加 request_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        else:
            log_data["request_id"] = current_request_id.get()
        
        # 添加可选字段
        for field in ("user_id", "duration", "status_code", "method", "path", "client_ip"):
            if hasattr(record, field):
                log_data[field] = getattr(record, field)
        
        # 异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    彩色控制台输出（开发环境）
    
    让日志更易读，快速区分级别
    """
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    def format(self, record: logging.LogRecord) -> str:
        # 保存原始 levelname
        original_levelname = record.levelname
        
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{self.BOLD}{record.levelname}{self.RESET}"
        
        # 添加 request_id
        request_id = getattr(record, "request_id", current_request_id.get())
        record.request_id = request_id[:8] if len(request_id) > 8 else request_id
        
        # 格式化
        formatted = super().format(record)
        
        # 恢复 levelname
        record.levelname = original_levelname
        
        return formatted


class RequestIDFilter(logging.Filter):
    """自动添加 request_id 到日志记录"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = current_request_id.get()
        return True


def setup_logging() -> None:
    """
    配置日志系统
    
    策略：
    - 开发环境：彩色控制台 + 文本文件
    - 生产环境：JSON 文件（便于日志聚合）
    """
    # 获取日志目录
    log_dir = get_log_dir()
    
    # 根日志配置
    # 根据LOG_LEVEL环境变量或DEBUG设置日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG if settings.DEBUG else logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除已有的 handlers
    root_logger.handlers.clear()
    
    # === 控制台 Handler ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.addFilter(RequestIDFilter())
    
    if settings.is_development:
        # 开发环境：彩色输出
        console_handler.setFormatter(ColoredFormatter(
            fmt="%(asctime)s | %(levelname)-17s | [%(request_id)s] %(name)-25s | %(message)s",
            datefmt="%H:%M:%S"
        ))
    else:
        # 生产环境：简洁输出
        console_handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    root_logger.addHandler(console_handler)
    
    # === 文件 Handler - 应用日志 ===
    if settings.is_production:
        # 生产环境：JSON 格式 + 按天轮转
        app_handler = TimedRotatingFileHandler(
            filename=log_dir / "app.log",
            when="midnight",
            interval=1,
            backupCount=30,  # 保留 30 天
            encoding="utf-8"
        )
        app_handler.setFormatter(JSONFormatter())
    else:
        # 开发环境：文本格式 + 按大小轮转
        app_handler = RotatingFileHandler(
            filename=log_dir / "app.log",
            maxBytes=settings.LOG_FILE_MAX_BYTES,
            backupCount=settings.LOG_FILE_BACKUP_COUNT,
            encoding="utf-8"
        )
        app_handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(request_id)s] %(name)-30s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    app_handler.setLevel(logging.INFO)
    app_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(app_handler)
    
    # === 文件 Handler - 错误日志 ===
    error_handler = RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=settings.LOG_FILE_MAX_BYTES,
        backupCount=10,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(RequestIDFilter())
    
    if settings.is_production:
        error_handler.setFormatter(JSONFormatter())
    else:
        error_handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(request_id)s] %(name)s\n"
                "%(pathname)s:%(lineno)d\n%(message)s\n",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    root_logger.addHandler(error_handler)
    
    # === 访问日志（独立文件）===
    _setup_access_logger(log_dir)
    
    # === 屏蔽第三方库的过多日志 ===
    for lib in ("urllib3", "httpx", "httpcore", "asyncio", "uvicorn", 
                "uvicorn.access", "sqlalchemy.engine", "openai", "httpx"):
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    root_logger.info(f"✅ Logging initialized | dir={log_dir} | env={settings.ENVIRONMENT.value}")


def _setup_access_logger(log_dir: Path) -> None:
    """配置访问日志（独立处理）"""
    access_logger = logging.getLogger("api.access")
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False  # 不传播到 root logger
    
    access_handler = TimedRotatingFileHandler(
        filename=log_dir / "access.log",
        when="midnight",
        interval=1,
        backupCount=7,  # 保留 7 天
        encoding="utf-8"
    )
    
    if settings.is_production:
        access_handler.setFormatter(JSONFormatter())
    else:
        access_handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    access_logger.addHandler(access_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取 logger 实例
    
    用法：
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("message")
    """
    return logging.getLogger(name)


class RequestLogger:
    """
    请求日志器
    
    用于中间件记录：请求ID、方法、路径、状态码、耗时
    """
    
    def __init__(self):
        self.logger = get_logger("api.access")
    
    def log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        client_ip: Optional[str] = None,
        user_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """记录 HTTP 请求日志"""
        
        # 构建日志消息
        message = f"{method} {path} - {status_code} - {duration:.3f}s"
        if client_ip:
            message = f"{client_ip} | {message}"
        
        # 根据状态码选择日志级别
        if status_code >= 500:
            level = logging.ERROR
        elif status_code >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO
        
        # 额外字段
        extra = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
        }
        
        if client_ip:
            extra["client_ip"] = client_ip
        if user_id:
            extra["user_id"] = user_id
        if error:
            extra["error"] = error
        
        self.logger.log(level, message, extra=extra)


def set_request_id(request_id: str) -> None:
    """设置当前请求的 request_id（供中间件调用）"""
    current_request_id.set(request_id)


def get_request_id() -> str:
    """获取当前请求的 request_id"""
    return current_request_id.get()


# 全局实例
request_logger = RequestLogger()
