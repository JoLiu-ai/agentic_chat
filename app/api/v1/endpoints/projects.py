"""
Project API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.project import ProjectService

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    user_id: str = "default_user"
    description: Optional[str] = None
    color: str = "blue"
    icon: str = "📁"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

@router.get("/projects")
async def get_projects(user_id: str = "default_user"):
    """获取所有项目"""
    try:
        projects = ProjectService.get_all_projects(user_id)
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/defaults")
async def get_default_projects():
    """获取默认项目模板"""
    return {"projects": ProjectService.get_default_projects()}

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """获取项目详情"""
    project = ProjectService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects")
async def create_project(project: ProjectCreate):
    """创建新项目"""
    try:
        project_id = ProjectService.create_project(
            name=project.name,
            user_id=project.user_id,
            description=project.description,
            color=project.color,
            icon=project.icon
        )
        return {"project_id": project_id, "message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}")
async def update_project(project_id: str, update: ProjectUpdate):
    """更新项目信息"""
    success = ProjectService.update_project(
        project_id=project_id,
        name=update.name,
        description=update.description,
        color=update.color,
        icon=update.icon
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or no updates made")
    
    return {"message": "Project updated successfully"}

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    success = ProjectService.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}
