"""
异常处理模块

定义自定义异常类和全局异常处理器
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """基础API异常类"""
    
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(BaseAPIException):
    """资源未找到异常"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(BaseAPIException):
    """验证错误异常"""
    
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationError(BaseAPIException):
    """认证错误异常"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(BaseAPIException):
    """授权错误异常"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class BadRequestError(BaseAPIException):
    """错误请求异常"""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ConflictError(BaseAPIException):
    """冲突错误异常"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class RateLimitError(BaseAPIException):
    """限流异常"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class DatabaseError(BaseAPIException):
    """数据库错误异常"""
    
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalServiceError(BaseAPIException):
    """外部服务错误异常"""
    
    def __init__(self, message: str = "External service error"):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    配置全局异常处理器
    
    处理顺序：
    1. 自定义API异常
    2. 请求验证错误
    3. 404错误
    4. 全局未捕获异常
    """
    
    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request: Request, exc: BaseAPIException):
        """自定义API异常处理器"""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            f"API Exception: {exc.message}",
            extra={"request_id": request_id, "status_code": exc.status_code}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "type": type(exc).__name__,
                "request_id": request_id,
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证错误处理器"""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"Validation error: {exc.errors()}",
            extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "type": "ValidationError",
                "request_id": request_id,
            }
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """404错误处理器"""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"Not found: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Path {request.url.path} not found",
                "type": "NotFoundError",
                "request_id": request_id,
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理器"""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            f"Unhandled exception: {exc}",
            extra={"request_id": request_id},
            exc_info=True
        )
        
        # 生产环境不暴露详细错误信息，开发环境显示完整错误
        if settings.is_production:
            detail = "An internal server error occurred"
        else:
            # 开发环境显示完整错误信息，包括堆栈
            import traceback
            detail = {
                "error": str(exc),
                "type": type(exc).__name__,
                "traceback": traceback.format_exc().split('\n')
            }
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": detail,
                "type": type(exc).__name__,
                "request_id": request_id,
            }
        )
    
    logger.info("✅ Exception handlers configured")

