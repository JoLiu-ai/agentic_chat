"""
Message Service - 消息管理服务（SQLAlchemy ORM版本）
支持树形结构：父节点、子节点、兄弟节点
"""
from typing import List, Optional, Dict
from app.db.database import get_db
from app.db.models import Message
from sqlalchemy import desc, func


class MessageService:
    """消息管理服务 - 支持树形结构"""
    
    @staticmethod
    def create_message(
        session_id: str,
        role: str,
        content: str,
        agent_type: Optional[str] = None,
        model: str = "gpt-4o",
        parent_id: Optional[int] = None,
        sibling_index: Optional[int] = None
    ) -> int:
        """
        创建新消息
        
        Args:
            session_id: 会话ID
            role: 消息角色 ('user' or 'assistant')
            content: 消息内容
            agent_type: Agent类型
            model: 模型名称
            parent_id: 父消息ID（用户消息为None，助手消息为用户消息ID）
            sibling_index: 兄弟节点索引（如果为None，自动计算）
        
        Returns:
            消息ID
        """
        with get_db() as db:
            # 如果是助手消息且有parent_id，需要计算sibling_index
            if role == 'assistant' and parent_id is not None and sibling_index is None:
                # 查找同一父节点下已有的子节点数量
                max_sibling = db.query(func.max(Message.sibling_index)).filter(
                    Message.parent_id == parent_id
                ).scalar()
                sibling_index = (max_sibling + 1) if max_sibling is not None else 0
            
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                agent_type=agent_type,
                model=model,
                parent_id=parent_id,
                sibling_index=sibling_index or 0
            )
            db.add(message)
            db.flush()  # Get the ID before commit
            message_id = message.message_id
        
        return message_id
    
    @staticmethod
    def find_user_message_by_content(session_id: str, content: str) -> Optional[int]:
        """
        查找相同内容的用户消息（用于版本分组）
        
        Args:
            session_id: 会话ID
            content: 消息内容
        
        Returns:
            用户消息ID，如果不存在则返回None
        """
        with get_db() as db:
            # 查找最后一个用户消息，且parent_id为NULL（根节点）
            message = db.query(Message).filter(
                Message.session_id == session_id,
                Message.role == 'user',
                Message.content == content,
                Message.parent_id.is_(None)
            ).order_by(Message.created_at.desc()).first()
            
            return message.message_id if message else None
    
    @staticmethod
    def get_session_messages(session_id: str) -> List[Dict]:
        """
        获取会话的所有消息（树形结构）
        返回扁平化的消息列表，包含树形关系信息
        """
        with get_db() as db:
            messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at).all()
            
            return [
                {
                    'id': str(m.message_id),  # 前端使用id字段
                    'message_id': m.message_id,
                    'session_id': m.session_id,
                    'role': m.role,
                    'content': m.content,
                    'agent_type': m.agent_type,
                    'model': m.model,
                    'created_at': m.created_at.isoformat(),
                    'parent_id': m.parent_id if m.parent_id is not None else None,
                    'sibling_index': m.sibling_index if m.sibling_index is not None else 0
                }
                for m in messages if m is not None
            ]
    
    @staticmethod
    def get_message_children(parent_id: int) -> List[Dict]:
        """
        获取指定消息的所有子节点（兄弟节点）
        
        Args:
            parent_id: 父消息ID
        
        Returns:
            子消息列表，按sibling_index排序
        """
        with get_db() as db:
            messages = db.query(Message).filter(
                Message.parent_id == parent_id
            ).order_by(Message.sibling_index).all()
            
            return [
                {
                    'id': str(m.message_id),
                    'message_id': m.message_id,
                    'session_id': m.session_id,
                    'role': m.role,
                    'content': m.content,
                    'agent_type': m.agent_type,
                    'model': m.model,
                    'created_at': m.created_at.isoformat(),
                    'parent_id': m.parent_id if m.parent_id is not None else None,
                    'sibling_index': m.sibling_index if m.sibling_index is not None else 0
                }
                for m in messages
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
