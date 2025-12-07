"""
应用生命周期事件

管理应用启动和关闭时需要执行的操作
"""
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def startup_event(app: FastAPI) -> None:
    """
    应用启动事件
    
    可以在这里添加：
    - 预热缓存
    - 初始化连接池
    - 注册服务发现
    - 加载模型等
    """
    # 存储应用级别的状态
    app.state.ready = True
    
    # 可以添加更多启动逻辑
    # 例如：预加载 AI 模型
    # await preload_models()
    
    logger.info("📦 Startup tasks completed")


async def shutdown_event(app: FastAPI) -> None:
    """
    应用关闭事件
    
    可以在这里添加：
    - 清理临时文件
    - 注销服务发现
    - 关闭外部连接
    - 保存状态等
    """
    app.state.ready = False
    
    # 可以添加更多清理逻辑
    # 例如：关闭 AI 模型连接
    # await cleanup_models()
    
    logger.info("🧹 Cleanup tasks completed")

