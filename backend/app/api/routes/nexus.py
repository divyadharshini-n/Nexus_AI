from fastapi import APIRouter

router = APIRouter()

# Nexus AI endpoints will be implemented later
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.conversation_repository import ConversationRepository
from app.schemas.nexus_schemas import NexusChatRequest, NexusChatResponse
from app.core.ai_agents.nexus_ai.nexus_main_agent import nexus_agent

router = APIRouter()


@router.post("/chat", response_model=NexusChatResponse)
async def nexus_chat(
    request: NexusChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with Nexus AI for PLC code generation
    """
    # Verify project ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(request.project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    # Get AI response
    result = await nexus_agent.chat(
        user_message=request.message,
        project_context=None  # Will add stage context later
    )
    
    # Save conversation to database
    conv_repo = ConversationRepository(db)
    
    # Save user message
    conv_repo.create(
        project_id=request.project_id,
        message_role="user",
        message_content=request.message
    )
    
    # Save AI response
    conv_repo.create(
        project_id=request.project_id,
        message_role="nexus_ai",
        message_content=result["message"]
    )
    
    return NexusChatResponse(
        response=result["message"],
        phase=result["phase"],
        manual_context_used=result["manual_context_used"]
    )