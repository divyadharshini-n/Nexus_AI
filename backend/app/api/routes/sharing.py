from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.db.models.user import User, UserRole
from app.db.models.project import Project
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.project_share_repository import ProjectShareRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.project_share_schemas import ShareProjectRequest, UnshareProjectRequest, ProjectShareResponse, SharedUserResponse

router = APIRouter()


def require_project_owner(current_user: User, project: Project):
    """Check if user is project owner or admin"""
    if current_user.role != UserRole.ADMIN and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner or admin can manage sharing"
        )


@router.post("/projects/{project_id}/share", response_model=ProjectShareResponse)
async def share_project(
    project_id: int,
    request: ShareProjectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Share project with an employee"""
    project_repo = ProjectRepository(db)
    share_repo = ProjectShareRepository(db)
    user_repo = UserRepository(db)
    
    # Get project
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    require_project_owner(current_user, project)
    
    # Check if user exists and is an employee
    shared_with_user = user_repo.get_by_id(request.user_id)
    if not shared_with_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if shared_with_user.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=400, detail="Can only share with employees")
    
    # Cannot share with owner
    if shared_with_user.id == project.owner_id:
        raise HTTPException(status_code=400, detail="Cannot share project with owner")
    
    # Share project
    share = share_repo.share_project(project_id, request.user_id, current_user.id)
    
    return ProjectShareResponse(
        id=share.id,
        project_id=share.project_id,
        shared_with=SharedUserResponse(
            id=shared_with_user.id,
            username=shared_with_user.username,
            full_name=shared_with_user.full_name,
            email=shared_with_user.email
        ),
        shared_at=share.created_at
    )


@router.delete("/projects/{project_id}/share/{user_id}")
async def unshare_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove project share"""
    project_repo = ProjectRepository(db)
    share_repo = ProjectShareRepository(db)
    
    # Get project
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    require_project_owner(current_user, project)
    
    # Unshare
    success = share_repo.unshare_project(project_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Share not found")
    
    return {"message": "Project unshared successfully"}


@router.get("/projects/{project_id}/shares", response_model=List[ProjectShareResponse])
async def get_project_shares(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all shares for a project"""
    project_repo = ProjectRepository(db)
    share_repo = ProjectShareRepository(db)
    user_repo = UserRepository(db)
    
    # Get project
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    require_project_owner(current_user, project)
    
    # Get shares
    shares = share_repo.get_project_shares(project_id)
    
    # Build response with usernames
    response = []
    for share in shares:
        user = user_repo.get_by_id(share.shared_with_user_id)
        if user:
            response.append(ProjectShareResponse(
                id=share.id,
                project_id=share.project_id,
                shared_with=SharedUserResponse(
                    id=user.id,
                    username=user.username,
                    full_name=user.full_name,
                    email=user.email
                ),
                shared_at=share.created_at
            ))
    
    return response
