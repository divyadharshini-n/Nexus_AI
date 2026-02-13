from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class SafetyManual(Base):
    __tablename__ = "safety_manuals"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    is_embedded = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)