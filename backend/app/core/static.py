"""
静态文件服务模块

管理静态文件的挂载和服务
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, get_static_path
from app.core.logging import get_logger

logger = get_logger(__name__)


def mount_static_files(app: FastAPI) -> None:
    """
    挂载静态文件目录
    
    注意：生产环境建议使用 Nginx 直接服务静态文件
    """
    static_path = get_static_path()
    
    if static_path.exists() and static_path.is_dir():
        app.mount(
            "/static",
            StaticFiles(directory=str(static_path)),
            name="static"
        )
        logger.info(f"📁 Static files mounted: {static_path}")
    else:
        logger.warning(f"⚠️  Static directory not found: {static_path}")

