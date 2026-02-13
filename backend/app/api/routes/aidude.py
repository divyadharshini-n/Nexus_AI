from fastapi import APIRouter

router = APIRouter()

# AI Dude endpoints will be implemented later
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.conversation_repository import ConversationRepository
from app.schemas.aidude_schemas import AIDudeQueryRequest, AIDudeQueryResponse
from app.core.ai_agents.ai_dude.aidude_main_agent import aidude_agent

router = APIRouter()


@router.post("/query", response_model=AIDudeQueryResponse)
async def aidude_query(
    request: AIDudeQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query AI Dude for explanations and guidance
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
    result = await aidude_agent.query(
        user_question=request.question,
        code_context=request.code_context
    )
    
    # Save conversation
    conv_repo = ConversationRepository(db)
    
    # Save user question
    conv_repo.create(
        project_id=request.project_id,
        message_role="user",
        message_content=request.question
    )
    
    # Save AI response
    conv_repo.create(
        project_id=request.project_id,
        message_role="ai_dude",
        message_content=result["answer"]
    )
    
    return AIDudeQueryResponse(
        answer=result["answer"],
        manual_grounded=result["manual_grounded"]
    )