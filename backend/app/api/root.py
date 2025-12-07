"""
根路由模块（前后端分离版本）

纯 API 服务，不提供前端页面
"""
from fastapi import FastAPI
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_root_routes(app: FastAPI) -> None:
    """注册根级别路由（纯 API）"""
    
    @app.get("/", tags=["Root"], summary="API 根路径")
    async def read_root() -> Dict[str, Any]:
        """
        API 根路径
        
        返回 API 基本信息和文档链接
        前端应用请访问: {FRONTEND_URL}
        """
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "version": settings.VERSION,
            "description": settings.DESCRIPTION,
            "docs_url": "/docs" if settings.DOCS_ENABLED else None,
            "redoc_url": "/redoc" if settings.DOCS_ENABLED else None,
            "openapi_url": f"{settings.API_V1_STR}/openapi.json" if settings.OPENAPI_ENABLED else None,
            "frontend_url": settings.FRONTEND_URL,
            "api_base": settings.API_V1_STR,
        }
    
    @app.get("/health", tags=["Health"], summary="健康检查")
    async def health_check() -> Dict[str, Any]:
        """
        健康检查端点
        
        用于：
        - 负载均衡器健康检查
        - Kubernetes liveness/readiness probe
        - 监控系统检测
        - Docker 健康检查
        """
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT.value,
            "ready": getattr(app.state, "ready", False),
        }
    
    @app.get("/ping", tags=["Health"], summary="简单 Ping")
    async def ping() -> Dict[str, str]:
        """简单的 ping 端点（最小响应）"""
        return {"ping": "pong"}
    
    @app.get("/info", tags=["Info"], summary="应用信息")
    async def app_info() -> Dict[str, Any]:
        """
        应用详细信息
        
        返回应用配置、版本、环境等信息
        """
        return {
            "application": {
                "name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "description": settings.DESCRIPTION,
            },
            "environment": {
                "mode": settings.ENVIRONMENT.value,
                "debug": settings.DEBUG,
            },
            "api": {
                "base_url": settings.API_V1_STR,
                "docs_enabled": settings.DOCS_ENABLED,
                "openapi_enabled": settings.OPENAPI_ENABLED,
            },
            "features": {
                "cors_enabled": settings.CORS_ENABLED,
                "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
                "gzip_enabled": settings.GZIP_ENABLED,
            },
            "frontend": {
                "url": settings.FRONTEND_URL,
            }
        }
    
    logger.info("✅ Root routes registered (API-only mode)")
