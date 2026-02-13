from sqlalchemy import Column, Integer, DateTime, ForeignKey, Interval
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    session_start = Column(DateTime, default=datetime.utcnow, index=True)
    session_end = Column(DateTime, nullable=True)
    duration = Column(Interval, nullable=True)
    interaction_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="sessions")