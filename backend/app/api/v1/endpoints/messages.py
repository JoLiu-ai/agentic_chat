"""
Message API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.message import MessageService

router = APIRouter()

class MessageCreate(BaseModel):
    session_id: str
    role: str
    content: str
    agent_type: Optional[str] = None
    model: Optional[str] = None

class MessageUpdate(BaseModel):
    content: str

@router.post("/messages")
async def create_message(message: MessageCreate):
    """创建新消息"""
    try:
        message_id = MessageService.create_message(
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            agent_type=message.agent_type,
            model=message.model
        )
        return {"message_id": message_id, "message": "Message created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/messages/{message_id}")
async def update_message(message_id: str, update: MessageUpdate):
    """更新消息内容"""
    success = MessageService.update_message_content(message_id, update.content)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message updated successfully"}

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str):
    """删除消息"""
    success = MessageService.delete_message(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}

@router.delete("/messages/{message_id}/after")
async def delete_messages_after(message_id: str):
    """删除某条消息之后的所有消息（用于编辑功能）"""
    try:
        MessageService.delete_messages_after(message_id)
        return {"message": "Messages deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
