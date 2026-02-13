from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class ProjectShare(Base):
    __tablename__ = "project_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shared_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ensure a project can't be shared with the same user twice
    __table_args__ = (UniqueConstraint('project_id', 'shared_with_user_id', name='_project_user_uc'),)
    
    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    shared_with = relationship("User", foreign_keys=[shared_with_user_id])
    shared_by = relationship("User", foreign_keys=[shared_by_user_id])
