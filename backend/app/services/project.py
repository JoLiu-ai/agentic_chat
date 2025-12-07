"""
Project Service - 项目管理服务（SQLAlchemy ORM版本）
"""
from typing import List, Optional, Dict
import uuid
from app.db.database import get_db
from app.db.models import Project
from sqlalchemy import desc


class ProjectService:
    """项目管理服务"""
    
    @staticmethod
    def create_project(
        name: str,
        description: Optional[str] = None,
        color: str = "blue",
        icon: str = "📁"
    ) -> str:
        """创建新项目"""
        project_id = f"project_{uuid.uuid4().hex[:16]}"
        
        with get_db() as db:
            project = Project(
                project_id=project_id,
                name=name,
                description=description,
                color=color,
                icon=icon
            )
            db.add(project)
        
        return project_id
    
    @staticmethod
    def get_all_projects() -> List[Dict]:
        """获取所有项目"""
        with get_db() as db:
            projects = db.query(Project).order_by(
                desc(Project.created_at)
            ).all()
            
            return [
                {
                    'project_id': p.project_id,
                    'name': p.name,
                    'description': p.description,
                    'color': p.color,
                    'icon': p.icon,
                    'created_at': p.created_at.isoformat(),
                    'session_count': len(p.sessions)
                }
                for p in projects
            ]
    
    @staticmethod
    def get_project(project_id: str) -> Optional[Dict]:
        """获取单个项目"""
        with get_db() as db:
            project = db.query(Project).filter(
                Project.project_id == project_id
            ).first()
            
            if not project:
                return None
            
            return {
                'project_id': project.project_id,
                'name': project.name,
                'description': project.description,
                'color': project.color,
                'icon': project.icon,
                'created_at': project.created_at.isoformat()
            }
    
    @staticmethod
    def update_project(
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None
    ) -> bool:
        """更新项目信息"""
        with get_db() as db:
            project = db.query(Project).filter(
                Project.project_id == project_id
            ).first()
            
            if not project:
                return False
            
            if name is not None:
                project.name = name
            if description is not None:
                project.description = description
            if color is not None:
                project.color = color
            if icon is not None:
                project.icon = icon
            
            return True
    
    @staticmethod
    def delete_project(project_id: str) -> bool:
        """删除项目"""
        with get_db() as db:
            project = db.query(Project).filter(
                Project.project_id == project_id
            ).first()
            
            if not project:
                return False
            
            # Set sessions' project_id to None before deleting
            for session in project.sessions:
                session.project_id = None
            
            db.delete(project)
            return True
    
    @staticmethod
    def get_default_projects() -> List[Dict]:
        """获取默认项目模板"""
        return [
            {"name": "工作", "color": "blue", "icon": "💼"},
            {"name": "学习", "color": "green", "icon": "📚"},
            {"name": "个人", "color": "purple", "icon": "🌟"},
            {"name": "研究", "color": "orange", "icon": "🔬"}
        ]
