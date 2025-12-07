"""
Agentic Chat API - Main Application

生产级FastAPI应用入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import setup_middleware
from app.core.exceptions import setup_exception_handlers
from app.api.v1.api import api_router
from app.db.database import init_db, close_db
from app.core.events import startup_event, shutdown_event

# 初始化日志
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # === Startup ===
    logger.info("🚀 Starting Agentic Chat API")
    
    try:
        # 初始化数据库
        init_db()
        logger.info("✅ Database initialized")
        
        # 执行启动事件
        await startup_event(app)
        
        logger.info("🎉 Application started successfully")
        logger.info(f"📝 Environment: {settings.ENVIRONMENT.value}")
        logger.info(f"🔧 Debug mode: {settings.DEBUG}")
        logger.info(f"📚 API docs: http://localhost:{settings.PORT}/docs")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise
    
    yield
    
    # === Shutdown ===
    logger.info("👋 Shutting down Agentic Chat API")
    
    try:
        # 执行关闭事件
        await shutdown_event(app)

        # 关闭数据库连接
        close_db()
        logger.info("✅ Database connections closed")
        
        logger.info("✅ Application shutdown complete")
        
    except Exception as e:
        logger.error(f"⚠️  Error during shutdown: {e}", exc_info=True)


def create_application() -> FastAPI:
    """
    应用工厂函数
    
    优点：
    - 方便测试（可以创建多个实例）
    - 易于集成（如ASGI服务器）
    - 清晰的配置流程
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.OPENAPI_ENABLED else None,
        docs_url="/docs" if settings.DOCS_ENABLED else None,
        redoc_url="/redoc" if settings.DOCS_ENABLED else None,
        lifespan=lifespan,
        debug=settings.DEBUG
    )
    
    # 设置中间件（按执行顺序）
    setup_middleware(application)
    
    # 设置异常处理器
    setup_exception_handlers(application)

    # 注册API路由
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # 挂载静态文件（生产环境建议用Nginx）
    if settings.SERVE_STATIC:
        from app.core.static import mount_static_files
        mount_static_files(application)
    
    # 注册根路由
    from app.api.root import setup_root_routes
    setup_root_routes(application)
    
    return application


# 创建应用实例
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    # 开发环境配置
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None,  # 使用我们自己的日志配置
        access_log=True
    )
