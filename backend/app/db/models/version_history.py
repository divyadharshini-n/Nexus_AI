from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class VersionLevel(str, enum.Enum):
    EVENT = "event"
    SESSION = "session"
    CHECKPOINT = "checkpoint"


class VersionHistory(Base):
    __tablename__ = "version_history"
    
    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey("generated_codes.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    level = Column(Enum(VersionLevel), nullable=False)
    version_number = Column(String(50), nullable=True)
    
    # Code snapshots
    old_code = Column(Text, nullable=True)
    new_code = Column(Text, nullable=True)
    diff = Column(Text, nullable=True)
    
    # Session grouping
    session_id = Column(Integer, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    version_metadata = Column(JSON, nullable=True)
    
    # Relationships
    code = relationship("GeneratedCode", back_populates="version_history")
    stage = relationship("Stage", foreign_keys=[stage_id])
    user = relationship("User")