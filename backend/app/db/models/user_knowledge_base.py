from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from datetime import datetime
from app.db.base import Base


class UserKnowledgeBase(Base):
    __tablename__ = "user_knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    concept_name = Column(String(255), nullable=False, index=True)
    concept_description = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    source = Column(String(255), nullable=True)
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)