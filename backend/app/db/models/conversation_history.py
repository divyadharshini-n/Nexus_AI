from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    NEXUS_AI = "nexus_ai"
    AI_DUDE = "ai_dude"
    SYSTEM = "system"


class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    message_role = Column(Enum(MessageRole), nullable=False)
    message_content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Store phase info, file references, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="conversations")