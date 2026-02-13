from fastapi import APIRouter

router = APIRouter()

# Planner endpoints will be implemented later
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.stage_repository import StageRepository
from app.schemas.planner_schemas import CreatePlanRequest, CreatePlanResponse
from app.core.planner.planner_orchestrator import planner_orchestrator

router = APIRouter()


@router.post("/create-plan", response_model=CreatePlanResponse)
async def create_plan(
    request: CreatePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create execution plan from control logic
    """
    try:
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
        
        # Create plan
        plan = await planner_orchestrator.create_plan(request.control_logic)
        
        if not plan['success']:
            return CreatePlanResponse(
                success=False,
                error=plan['error']
            )
        
        # Save stages to database
        stage_repo = StageRepository(db)
        
        # Delete existing stages for this project
        stage_repo.delete_project_stages(request.project_id)
        
        # Create new stages
        for stage_data in plan['stages']:
            stage_repo.create(
                project_id=request.project_id,
                stage_number=stage_data['stage_number'],
                stage_name=stage_data['stage_name'],
                stage_type=stage_data['stage_type'],
                description=stage_data.get('description', ''),
                original_logic=stage_data['original_logic']
            )
        
        return CreatePlanResponse(
            success=True,
            analysis=plan['analysis'],
            stages=plan['stages'],
            dependencies=plan['dependencies'],
            dependency_validation=plan['dependency_validation'],
            transition_graph=plan['transition_graph'],
            total_stages=plan['total_stages']
        )
    except Exception as e:
        import traceback
        print(f"Create plan error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create plan: {str(e)}"
        )


@router.get("/stages/{project_id}")
async def get_project_stages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stages for a project"""
    # Verify project ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get stages
    stage_repo = StageRepository(db)
    stages = stage_repo.get_project_stages(project_id)
    
    return {"stages": stages}