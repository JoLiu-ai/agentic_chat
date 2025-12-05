"""
Session Service - 会话管理服务（SQLAlchemy ORM版本）
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import json
from app.db.database import get_db
from app.db.models import Session, Message
from sqlalchemy import desc


class SessionService:
    """会话管理服务"""
    
    @staticmethod
    def create_session(
        user_id: str = "default_user",
        title: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> str:
        """创建新会话"""
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        
        with get_db() as db:
            new_session = Session(
                session_id=session_id,
                user_id=user_id,
                title=title or "新对话",
                project_id=project_id
            )
            db.add(new_session)
        
        return session_id
    
    @staticmethod
    def get_all_sessions(user_id: str = "default_user") -> List[Dict]:
        """获取所有会话"""
        with get_db() as db:
            sessions = db.query(Session).filter(
                Session.user_id == user_id
            ).order_by(desc(Session.updated_at)).all()
            
            result = []
            for s in sessions:
                session_dict = {
                    'session_id': s.session_id,
                    'title': s.title,
                    'created_at': s.created_at.isoformat(),
                    'updated_at': s.updated_at.isoformat(),
                    'is_starred': s.is_starred,
                    'project_id': s.project_id,
                    'tags': json.loads(s.tags) if s.tags else None,
                    'project_name': s.project.name if s.project else None,
                    'project_color': s.project.color if s.project else None,
                    'last_message': None
                }
                
                # Safely get last message
                try:
                    if s.messages is not None and len(s.messages) > 0:
                        last_msg = s.messages[-1]
                        if last_msg is not None:
                            session_dict['last_message'] = last_msg.content
                except (AttributeError, IndexError):
                    pass
                
                result.append(session_dict)
            
            return result
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """获取单个会话详情"""
        with get_db() as db:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if not session:
                return None
            
            return {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'title': session.title,
                'project_id': session.project_id,
                'is_starred': session.is_starred,
                'tags': json.loads(session.tags) if session.tags else None,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            }
    
    @staticmethod
    def update_session(
        session_id: str,
        title: Optional[str] = None,
        is_starred: Optional[bool] = None,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """更新会话信息"""
        with get_db() as db:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            if title is not None:
                session.title = title
            
            if is_starred is not None:
                session.is_starred = is_starred
            
            if project_id is not None:
                session.project_id = project_id
            
            if tags is not None:
                session.tags = json.dumps(tags)
            
            session.updated_at = datetime.utcnow()
            
            return True
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """删除会话（级联删除消息）"""
        with get_db() as db:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            db.delete(session)
            return True
    
    @staticmethod
    def get_starred_sessions(user_id: str = "default_user") -> List[Dict]:
        """获取收藏的会话"""
        with get_db() as db:
            sessions = db.query(Session).filter(
                Session.user_id == user_id,
                Session.is_starred == True
            ).order_by(desc(Session.updated_at)).all()
            
            return [
                {
                    'session_id': s.session_id,
                    'title': s.title,
                    'created_at': s.created_at.isoformat(),
                    'updated_at': s.updated_at.isoformat(),
                    'is_starred': s.is_starred
                }
                for s in sessions
            ]
    
    @staticmethod
    def get_project_sessions(project_id: str) -> List[Dict]:
        """获取项目下的所有会话"""
        with get_db() as db:
            sessions = db.query(Session).filter(
                Session.project_id == project_id
            ).order_by(desc(Session.updated_at)).all()
            
            return [
                {
                    'session_id': s.session_id,
                    'title': s.title,
                    'created_at': s.created_at.isoformat(),
                    'updated_at': s.updated_at.isoformat()
                }
                for s in sessions
            ]
    
    @staticmethod
    def update_session_timestamp(session_id: str):
        """更新会话时间戳"""
        with get_db() as db:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if session:
                session.updated_at = datetime.utcnow()
    
    @staticmethod
    def auto_generate_title(session_id: str, first_message: str):
        """自动生成会话标题"""
        # 清理消息文本
        title = first_message.strip()
        
        # 移除换行符
        title = title.replace('\n', ' ')
        
        # 限制长度到40个字符
        if len(title) > 40:
            title = title[:40] + "..."
        
        # 如果太短，使用默认标题
        if len(title) < 3:
            title = "新对话"
        
        SessionService.update_session(session_id, title=title)
        print(f"✅ Auto-generated title for {session_id}: {title}")
