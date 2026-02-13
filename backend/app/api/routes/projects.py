from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.api.deps import get_current_user
from app.schemas.project_schemas import ProjectCreate, ProjectResponse
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.project_share_repository import ProjectShareRepository
from app.db.models.user import User, UserRole

router = APIRouter()


@router.post("/create", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new project"""
    project_repo = ProjectRepository(db)
    
    project = project_repo.create(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )
    
    return project


@router.get("/list", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects for current user (role-based)"""
    from app.db.repositories.user_repository import UserRepository
    
    project_repo = ProjectRepository(db)
    user_repo = UserRepository(db)
    
    # Admin sees all projects
    if current_user.role == UserRole.ADMIN:
        projects = project_repo.get_all_projects()
    else:
        # Employee sees own + shared projects
        projects = project_repo.get_user_projects(current_user.id)
    
    # Add owner username to response
    response = []
    for project in projects:
        project_dict = ProjectResponse.model_validate(project).model_dump()
        owner = user_repo.get_by_id(project.owner_id)
        project_dict['owner_username'] = owner.username if owner else None
        response.append(project_dict)
    
    return response


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project by ID"""
    project_repo = ProjectRepository(db)
    share_repo = ProjectShareRepository(db)
    project = project_repo.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Admin can access all projects
    if current_user.role == UserRole.ADMIN:
        return project
    
    # Check if user is owner or has shared access
    is_owner = project.owner_id == current_user.id
    is_shared = share_repo.get_share(project_id, current_user.id) is not None
    
    if not (is_owner or is_shared):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete project (with all related data)"""
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Admin can delete any project, employees only their own
    if current_user.role != UserRole.ADMIN and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    # Hard delete (cascades to all related data due to relationships)
    project_repo.hard_delete(project_id)
    
    return None