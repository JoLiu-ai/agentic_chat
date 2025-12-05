from fastapi import APIRouter
from app.api.v1.endpoints import chat, router_monitor, sessions, projects, messages

api_router = APIRouter()
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(router_monitor.router, prefix="/router", tags=["monitoring"])
api_router.include_router(sessions.router, tags=["sessions"])
api_router.include_router(projects.router, tags=["projects"])
api_router.include_router(messages.router, tags=["messages"])
