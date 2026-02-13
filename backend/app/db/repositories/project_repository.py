from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db.models.project import Project, ProjectStatus
from app.db.models.project_share import ProjectShare
from app.db.models.user import User, UserRole


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str, owner_id: int, description: Optional[str] = None) -> Project:
        """Create new project"""
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
            status=ProjectStatus.ACTIVE
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_user_projects(self, user_id: int) -> List[Project]:
        """Get all projects for a user (owned + shared)"""
        return self.db.query(Project).filter(
            or_(
                Project.owner_id == user_id,
                Project.id.in_(
                    self.db.query(ProjectShare.project_id).filter(
                        ProjectShare.shared_with_user_id == user_id
                    )
                )
            ),
            Project.status != ProjectStatus.DELETED
        ).order_by(Project.created_at.desc()).all()
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects (admin view)"""
        return self.db.query(Project).filter(
            Project.status != ProjectStatus.DELETED
        ).order_by(Project.created_at.desc()).all()
    
    def delete(self, project_id: int):
        """Delete project (soft delete)"""
        project = self.get_by_id(project_id)
        if project:
            project.status = ProjectStatus.DELETED
            self.db.commit()
    
    def hard_delete(self, project_id: int):
        """Permanently delete project and all related data"""
        project = self.get_by_id(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()