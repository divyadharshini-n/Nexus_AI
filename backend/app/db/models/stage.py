from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Stage(Base):
    __tablename__ = "stages"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    stage_number = Column(Integer, nullable=False)
    stage_name = Column(String(255), nullable=False)
    stage_type = Column(String(100), nullable=False)  # idle, safety, validation, operation, etc.
    description = Column(Text, nullable=True)
    original_logic = Column(Text, nullable=False)  # Pure user logic
    edited_logic = Column(Text, nullable=True)  # User-edited logic
    is_validated = Column(Boolean, default=False)
    is_finalized = Column(Boolean, default=False)
    
    # Stage dependencies
    dependencies = Column(JSON, nullable=True)  # List of stage IDs this depends on
    entry_conditions = Column(JSON, nullable=True)
    exit_conditions = Column(JSON, nullable=True)
    
    # Safety validation
    safety_items = Column(JSON, nullable=True)  # Safety questions and responses
    safety_severity = Column(JSON, nullable=True)  # 🔴🟠🔵 tags
    
    # Version tracking
    version_number = Column(String(50), default="1.0.0")  # Semantic version
    last_action = Column(String(100), nullable=True)  # Last action performed
    last_action_timestamp = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="stages")
    generated_codes = relationship("GeneratedCode", back_populates="stage", cascade="all, delete-orphan")
    version_histories = relationship("VersionHistory", foreign_keys="[VersionHistory.stage_id]", cascade="all, delete-orphan")