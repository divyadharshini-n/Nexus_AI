from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from app.db.base import Base


class SystemPrompt(Base):
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)  # nexus_ai or ai_dude
    version = Column(String(50), nullable=False)
    prompt_content = Column(Text, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)