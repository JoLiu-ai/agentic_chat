"""
Session API Endpoints - Enhanced
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.session import SessionService
from app.services.message import MessageService

router = APIRouter()

class SessionCreate(BaseModel):
    user_id: str = "default_user"
    title: Optional[str] = None
    project_id: Optional[str] = None

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    is_starred: Optional[bool] = None
    project_id: Optional[str] = None
    tags: Optional[List[str]] = None

@router.get("/sessions")
async def get_sessions(user_id: str = "default_user"):
    """获取所有会话列表"""
    try:
        sessions = SessionService.get_all_sessions(user_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/starred")
async def get_starred_sessions(user_id: str = "default_user"):
    """获取收藏的会话"""
    try:
        sessions = SessionService.get_starred_sessions(user_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """获取会话的所有消息"""
    try:
        messages = MessageService.get_session_messages(session_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions")
async def create_session(session: SessionCreate):
    """创建新会话"""
    try:
        session_id = SessionService.create_session(
            user_id=session.user_id,
            title=session.title,
            project_id=session.project_id
        )
        return {"session_id": session_id, "message": "Session created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}")
async def update_session(session_id: str, update: SessionUpdate):
    """更新会话信息"""
    success = SessionService.update_session(
        session_id=session_id,
        title=update.title,
        is_starred=update.is_starred,
        project_id=update.project_id,
        tags=update.tags
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or no updates made")
    
    return {"message": "Session updated successfully"}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = SessionService.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}

@router.get("/sessions/project/{project_id}")
async def get_project_sessions(project_id: str):
    """获取项目下的所有会话"""
    try:
        sessions = SessionService.get_project_sessions(project_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
