from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.code_repository import CodeRepository
from app.core.code_generation.csv_export_engine import csv_export_engine

router = APIRouter()


@router.get("/csv/project/{project_id}")
async def export_project_csv(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export all project code to CSV
    """
    # Verify ownership
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
    
    # Get all generated codes
    code_repo = CodeRepository(db)
    codes = code_repo.get_project_codes(project_id)
    
    if not codes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No generated code found for this project"
        )
    
    # Prepare data
    project_data = {
        "project_name": project.name,
        "codes": []
    }
    
    for code in codes:
        project_data["codes"].append({
            "program_name": code.program_name,
            "execution_type": code.execution_type,
            "global_labels": code.global_labels or [],
            "local_labels": code.local_labels or [],
            "program_body": code.program_body or ""
        })
    
    # Generate CSV
    csv_content = csv_export_engine.export_project_code(project_data)
    
    # Create response
    csv_bytes = BytesIO(csv_content.encode('utf-8'))
    csv_bytes.seek(0)
    
    filename = f"{project.name.replace(' ', '_')}_code_export.csv"
    
    return StreamingResponse(
        csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/csv/stage/{stage_id}")
async def export_stage_csv(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export single stage code to CSV
    """
    # Get code
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(stage_id)
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No generated code found for this stage"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(code.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Prepare data
    stage_data = {
        "program_name": code.program_name,
        "execution_type": code.execution_type,
        "global_labels": code.global_labels or [],
        "local_labels": code.local_labels or [],
        "program_body": code.program_body or ""
    }
    
    # Generate CSV
    csv_content = csv_export_engine.export_stage_code(stage_data)
    
    # Create response
    csv_bytes = BytesIO(csv_content.encode('utf-8'))
    csv_bytes.seek(0)
    
    filename = f"{code.program_name}_export.csv"
    
    return StreamingResponse(
        csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )