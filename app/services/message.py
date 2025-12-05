"""
Message Service - 消息管理服务（SQLAlchemy ORM版本）
"""
from typing import List, Optional, Dict
from app.db.database import get_db
from app.db.models import Message
from sqlalchemy import desc


class MessageService:
    """消息管理服务"""
    
    @staticmethod
    def create_message(
        session_id: str,
        role: str,
        content: str,
        agent_type: Optional[str] = None,
        model: str = "gpt-4o"
    ) -> int:
        """创建新消息"""
        with get_db() as db:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                agent_type=agent_type,
                model=model
            )
            db.add(message)
            db.flush()  # Get the ID before commit
            message_id = message.message_id
        
        return message_id
    
    @staticmethod
    def get_session_messages(session_id: str) -> List[Dict]:
        """获取会话的所有消息"""
        with get_db() as db:
            messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at).all()
            
            return [
                {
                    'message_id': m.message_id,
                    'session_id': m.session_id,
                    'role': m.role,
                    'content': m.content,
                    'agent_type': m.agent_type,
                    'model': m.model,
                    'created_at': m.created_at.isoformat()
                }
                for m in messages if m is not None
            ]
    
    @staticmethod
    def get_message_count(session_id: str) -> int:
        """获取会话的消息数量"""
        with get_db() as db:
            count = db.query(Message).filter(
                Message.session_id == session_id
            ).count()
            return count
    
    @staticmethod
    def update_message(message_id: int, content: str) -> bool:
        """更新消息内容"""
        with get_db() as db:
            message = db.query(Message).filter(
                Message.message_id == message_id
            ).first()
            
            if not message:
                return False
            
            message.content = content
            return True
    
    @staticmethod
    def delete_message(message_id: int) -> bool:
        """删除单条消息"""
        with get_db() as db:
            message = db.query(Message).filter(
                Message.message_id == message_id
            ).first()
            
            if not message:
                return False
            
            db.delete(message)
            return True
    
    @staticmethod
    def delete_messages_after(message_id: int) -> bool:
        """删除指定消息之后的所有消息"""
        with get_db() as db:
            # Get the message to find its timestamp and session
            target_message = db.query(Message).filter(
                Message.message_id == message_id
            ).first()
            
            if not target_message:
                return False
            
            # Delete all messages after this one in the same session
            db.query(Message).filter(
                Message.session_id == target_message.session_id,
                Message.created_at > target_message.created_at
            ).delete(synchronize_session='fetch')
            
            return True
