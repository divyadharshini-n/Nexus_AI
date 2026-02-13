from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.project_share import ProjectShare
from app.db.models.user import User


class ProjectShareRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def share_project(self, project_id: int, shared_with_user_id: int, shared_by_user_id: int) -> ProjectShare:
        """Share a project with a user"""
        # Check if already shared
        existing = self.get_share(project_id, shared_with_user_id)
        if existing:
            return existing
        
        share = ProjectShare(
            project_id=project_id,
            shared_with_user_id=shared_with_user_id,
            shared_by_user_id=shared_by_user_id
        )
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share
    
    def unshare_project(self, project_id: int, shared_with_user_id: int) -> bool:
        """Remove project share"""
        share = self.get_share(project_id, shared_with_user_id)
        if share:
            self.db.delete(share)
            self.db.commit()
            return True
        return False
    
    def get_share(self, project_id: int, shared_with_user_id: int) -> Optional[ProjectShare]:
        """Get specific project share"""
        return self.db.query(ProjectShare).filter(
            ProjectShare.project_id == project_id,
            ProjectShare.shared_with_user_id == shared_with_user_id
        ).first()
    
    def get_project_shares(self, project_id: int) -> List[ProjectShare]:
        """Get all shares for a project"""
        return self.db.query(ProjectShare).filter(
            ProjectShare.project_id == project_id
        ).all()
    
    def get_shared_with_user(self, user_id: int) -> List[ProjectShare]:
        """Get all projects shared with a user"""
        return self.db.query(ProjectShare).filter(
            ProjectShare.shared_with_user_id == user_id
        ).all()
