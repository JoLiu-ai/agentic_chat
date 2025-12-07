"""
中间件系统

包括：请求ID追踪、性能监控、访问日志、CORS、限流、安全头、压缩
"""
import time
import uuid
from typing import Callable, Optional
from contextvars import ContextVar

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import request_logger, get_logger, set_request_id

logger = get_logger(__name__)

# 上下文变量（用于跨层访问）
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    请求ID中间件
    
    功能：
    - 为每个请求生成或获取唯一ID
    - 设置到上下文变量（全局可访问）
    - 在响应头中返回 X-Request-ID
    - 在日志中自动关联 request_id
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 从请求头获取或生成新的 request_id
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # 设置到上下文变量（供日志系统使用）
        request_id_var.set(request_id)
        set_request_id(request_id)
        
        # 添加到 request.state（方便其他地方访问）
        request.state.request_id = request_id
        
        # 处理请求
        response = await call_next(request)
        
        # 在响应头中返回
        response.headers["X-Request-ID"] = request_id
        
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """
    性能监控中间件
    
    功能：
    - 记录请求处理时间
    - 检测并告警慢请求
    - 在响应头中返回 X-Process-Time
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        duration = time.time() - start_time
        
        # 添加响应头
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        
        # 慢请求告警
        if duration > settings.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"🐢 慢请求: {request.method} {request.url.path} "
                f"耗时 {duration:.3f}s (阈值: {settings.SLOW_REQUEST_THRESHOLD}s)",
                extra={"duration": duration}
            )
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    访问日志中间件
    
    功能：
    - 记录所有 HTTP 请求到 access.log
    - 包含：方法、路径、状态码、耗时、客户端IP
    - 自动处理异常情况
    """
    
    # 排除的路径（不记录日志）
    EXCLUDE_PATHS = {"/health", "/metrics", "/favicon.ico"}
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实 IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过排除的路径和静态文件
        if (request.url.path in self.EXCLUDE_PATHS or 
            request.url.path.startswith("/static")):
            return await call_next(request)
        
        start_time = time.time()
        status_code = 500
        error: Optional[str] = None
        
        try:
            # 处理请求
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # 捕获异常但继续抛出
            error = str(e)
            raise
        finally:
            # 计算耗时
            duration = time.time() - start_time
            
            # 记录访问日志
            request_logger.log_request(
                request_id=getattr(request.state, "request_id", ""),
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration=duration,
                client_ip=self._get_client_ip(request),
                user_id=user_id_var.get() or None,
                error=error
            )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全响应头中间件
    
    功能：
    - 添加常见的安全响应头
    - 防止 XSS、点击劫持、MIME 嗅探等攻击
    - 移除服务器信息（避免暴露技术栈）
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS（仅生产环境，需要 HTTPS）
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        # 移除服务器信息
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    简单限流中间件（基于内存）
    
    功能：
    - 基于 IP 的速率限制
    - 滑动窗口算法
    - 返回限流响应头
    
    注意：生产环境建议使用 Redis + slowapi
    """
    
    def __init__(self, app):
        super().__init__(app)
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        self.requests = defaultdict(list)
        self.window = timedelta(minutes=1)
        self.max_requests = int(settings.RATE_LIMIT_DEFAULT.split("/")[0])
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, ip: str, now):
        """清理过期请求记录"""
        cutoff = now - self.window
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if req_time > cutoff
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过不需要限流的路径
        skip_paths = {"/health", "/docs", "/redoc", "/openapi.json"}
        if (request.url.path in skip_paths or 
            request.url.path.startswith("/static")):
            return await call_next(request)
        
        from datetime import datetime
        
        client_ip = self._get_client_ip(request)
        now = datetime.now()
        
        # 清理过期记录
        self._cleanup_old_requests(client_ip, now)
        
        # 检查限流
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(
                f"🚫 限流触发: IP {client_ip} 超过限制 ({self.max_requests}/分钟)"
            )
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                }
            )
        
        # 记录请求
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        
        # 添加限流信息到响应头
        remaining = max(0, self.max_requests - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """
    配置所有中间件
    
    注意：
    - 中间件执行顺序很重要！
    - 添加顺序 = 执行顺序（请求时）的反序
    - 最后添加的最先执行
    
    执行顺序（请求 → 响应）：
    1. RequestID - 生成追踪ID
    2. Timing - 开始计时
    3. Logging - 记录访问日志
    4. Security - 添加安全头
    5. Gzip - 压缩响应
    6. CORS - 跨域处理
    7. TrustedHost - 主机验证
    8. RateLimit - 限流检查
    """
    
    # === 8. 限流（最先执行，快速拒绝） ===
    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(RateLimitMiddleware)
        logger.info(f"✅ Rate limiting enabled: {settings.RATE_LIMIT_DEFAULT}")
    
    # === 7. 受信主机验证（生产环境） ===
    if settings.is_production and settings.ALLOWED_HOSTS != ["*"]:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
        logger.info(f"✅ Trusted host middleware enabled: {settings.ALLOWED_HOSTS}")
    
    # === 6. CORS ===
    if settings.CORS_ENABLED:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
            expose_headers=["X-Request-ID", "X-Process-Time"],
        )
        logger.info("✅ CORS middleware enabled")
    
    # === 5. Gzip 压缩 ===
    if settings.GZIP_ENABLED:
        app.add_middleware(
            GZipMiddleware,
            minimum_size=settings.GZIP_MIN_SIZE
        )
        logger.info(f"✅ Gzip compression enabled (min: {settings.GZIP_MIN_SIZE} bytes)")
    
    # === 4. 安全响应头 ===
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("✅ Security headers middleware enabled")
    
    # === 3. 访问日志 ===
    app.add_middleware(LoggingMiddleware)
    logger.info("✅ Logging middleware enabled")
    
    # === 2. 性能监控 ===
    app.add_middleware(TimingMiddleware)
    logger.info("✅ Timing middleware enabled")
    
    # === 1. 请求ID追踪（最后执行，确保所有请求都有ID） ===
    app.add_middleware(RequestIDMiddleware)
    logger.info("✅ Request ID middleware enabled")


def get_request_id() -> str:
    """获取当前请求的 request_id"""
    return request_id_var.get()


def set_user_id(user_id: str) -> None:
    """设置当前请求的 user_id（供认证中间件调用）"""
    user_id_var.set(user_id)


def get_user_id() -> str:
    """获取当前请求的 user_id"""
    return user_id_var.get()
