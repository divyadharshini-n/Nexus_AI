from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class ActivityType(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    PROJECT_CREATE = "project_create"
    PROJECT_DELETE = "project_delete"
    FILE_UPLOAD = "file_upload"
    AI_INTERACTION = "ai_interaction"
    PLANNING_STAGE = "planning_stage"
    VALIDATION = "validation"
    CODE_GENERATION = "code_generation"
    STAGE_EDIT = "stage_edit"
    RA_INTERROGATION = "ra_interrogation"
    EXPORT = "export"


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    activity_type = Column(Enum(ActivityType), nullable=False)
    description = Column(Text, nullable=False)
    activity_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    project = relationship("Project", back_populates="activity_logs")