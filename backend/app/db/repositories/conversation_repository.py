from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.conversation_history import ConversationHistory, MessageRole


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        project_id: int,
        message_role: str,
        message_content: str,
        metadata: Optional[dict] = None
    ) -> ConversationHistory:
        """Create conversation message"""
        conversation = ConversationHistory(
            project_id=project_id,
            message_role=MessageRole(message_role),
            message_content=message_content,
            message_metadata=metadata
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_project_history(
        self,
        project_id: int,
        limit: int = 50
    ) -> List[ConversationHistory]:
        """Get conversation history for a project"""
        return self.db.query(ConversationHistory).filter(
            ConversationHistory.project_id == project_id
        ).order_by(
            ConversationHistory.timestamp.desc()
        ).limit(limit).all()