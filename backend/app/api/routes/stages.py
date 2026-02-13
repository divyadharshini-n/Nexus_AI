from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.stage_repository import StageRepository
from app.db.repositories.project_repository import ProjectRepository
from app.schemas.stage_schemas import (
    UpdateStageLogicRequest,
    ValidateStageRequest,
    FinalizeStageRequest,
    ValidationResponse
)
from app.core.validation.stage_validator import stage_validator
from app.services.version_history_service import VersionHistoryService
from app.db.repositories.code_repository import CodeRepository
from app.core.reports.pdf_version_history_generator import PDFVersionHistoryGenerator

router = APIRouter()


@router.put("/update-logic")
async def update_stage_logic(
    request: UpdateStageLogicRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update stage logic (edit)
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(request.stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Update logic
    old_logic = stage.edited_logic or stage.original_logic
    stage_repo.update_logic(request.stage_id, request.edited_logic)
    
    # Track version history
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(stage.id)
    if code:
        version_service = VersionHistoryService(db)
        version_service.create_version_entry(
            code_id=code.id,
            stage_id=stage.id,
            user_id=current_user.id,
            action_type="edit_logic",
            old_data={"edited_logic": old_logic},
            new_data={"edited_logic": request.edited_logic},
            metadata={"description": "Stage logic edited"}
        )
    
    return {
        "success": True,
        "message": "Stage logic updated successfully"
    }


@router.post("/validate", response_model=ValidationResponse)
async def validate_stage(
    request: ValidateStageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate stage logic
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(request.stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Prepare stage data
    stage_data = {
        "id": stage.id,
        "stage_number": stage.stage_number,
        "stage_name": stage.stage_name,
        "stage_type": stage.stage_type,
        "original_logic": stage.original_logic,
        "edited_logic": stage.edited_logic
    }
    
    # Validate
    try:
        result = await stage_validator.validate_stage(stage_data)
        
        # If validation passed, mark stage as validated
        if result['valid']:
            stage_repo.mark_validated(stage.id)
            
            # Track version history
            code_repo = CodeRepository(db)
            code = code_repo.get_by_stage(stage.id)
            if code:
                version_service = VersionHistoryService(db)
                version_service.create_version_entry(
                    code_id=code.id,
                    stage_id=stage.id,
                    user_id=current_user.id,
                    action_type="validate",
                    metadata={
                        "description": "Stage validated",
                        "validation_status": result['status'],
                        "valid": result['valid']
                    }
                )
        
        return ValidationResponse(
            success=True,
            valid=result['valid'],
            status=result['status'],
            semantic_analysis=result.get('semantic_analysis', ''),
            logical_consistency=result.get('logical_consistency', ''),
            safety_compliance=result.get('safety_compliance', ''),
            issues=result.get('issues', []),
            recommendations=result.get('recommendations', []),
            categorized_issues=result.get('categorized_issues', [])
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Validation failed for stage {stage.id}: {str(e)}", exc_info=True)
        return ValidationResponse(
            success=False,
            valid=False,
            status="ERROR",
            semantic_analysis=f"Validation error occurred: {str(e)}",
            logical_consistency="Unable to perform validation due to error",
            safety_compliance="Unable to perform validation due to error",
            issues=["Validation system error occurred"],
            recommendations=["Please check backend logs and try again"],
            categorized_issues=[{
                'severity': 'critical',
                'title': 'Validation System Error',
                'description': 'An error occurred during validation',
                'recommended_logic': f'Please check backend logs. Error: {str(e)}'
            }],
            error=str(e)
        )


@router.post("/finalize")
async def finalize_stage(
    request: FinalizeStageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Finalize stage (lock it)
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(request.stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Check if validated
    if not stage.is_validated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage must be validated before finalizing"
        )
    
    # Finalize
    stage_repo.mark_finalized(request.stage_id)
    
    return {
        "success": True,
        "message": "Stage finalized successfully"
    }


@router.get("/{stage_id}/version-history")
async def get_stage_version_history(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get version history for a stage
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get version history
    version_service = VersionHistoryService(db)
    summary = version_service.get_version_summary(stage_id)
    
    return {
        "success": True,
        "stage_id": stage_id,
        "stage_name": stage.stage_name,
        **summary
    }


@router.get("/{stage_id}/version-history/download")
async def download_version_history_report(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download complete version history report for a stage
    """
    from fastapi.responses import FileResponse
    from app.core.reports.version_report_generator import version_report_generator
    
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get version history
    version_service = VersionHistoryService(db)
    history_data = version_service.get_stage_version_history(stage_id)
    
    # Generate report
    try:
        report_path = version_report_generator.generate_version_history_report(
            stage=stage,
            history=history_data,
            project_name=project.name
        )
        
        return FileResponse(
            path=report_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"Version_History_{stage.stage_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}"
        )


@router.get("/{stage_id}/version/{version_number}/download")
async def download_version_report(
    stage_id: int,
    version_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download report for a specific version of a stage
    """
    from fastapi.responses import FileResponse
    from app.core.reports.version_report_generator import version_report_generator
    
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get specific version
    version_service = VersionHistoryService(db)
    version_entry = version_service.get_version_by_number(stage_id, version_number)
    
    if not version_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found"
        )
    
    # Get code for this version
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(stage_id)
    
    # Generate report
    try:
        report_path = version_report_generator.generate_single_version_report(
            stage=stage,
            version=version_entry,
            code=code,
            project_name=project.name
        )
        
        return FileResponse(
            path=report_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{stage.stage_name}_v{version_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}"
        )


@router.get("/{stage_id}")
async def get_stage_detail(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed stage information
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return {
        "success": True,
        "stage": stage
    }


@router.get("/{stage_id}/version-history")
async def get_version_history(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get version history for a stage (JSON format for UI display)
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get version history with employee names
    version_service = VersionHistoryService(db)
    history = version_service.get_stage_version_history_with_employees(stage_id)
    
    return {
        "success": True,
        "stage": {
            "id": stage.id,
            "stage_name": stage.stage_name,
            "stage_number": stage.stage_number,
            "version_number": stage.version_number,
            "last_action": stage.last_action,
            "last_action_timestamp": stage.last_action_timestamp.isoformat() if stage.last_action_timestamp else None
        },
        "history": history,
        "total_count": len(history)
    }


@router.get("/{stage_id}/version-history-pdf")
async def get_version_history_pdf(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and download PDF version history report for a stage
    """
    # Get stage
    stage_repo = StageRepository(db)
    stage = stage_repo.get_by_id(stage_id)
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    # Verify ownership
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(stage.project_id)
    
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get version history with employee names
    version_service = VersionHistoryService(db)
    history = version_service.get_stage_version_history_with_employees(stage_id)
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No version history found for this stage"
        )
    
    # Create employee names mapping
    employee_names = {
        h['user_id']: h['employee_name']
        for h in history
    }
    
    # Convert stage to dict for PDF generator
    stage_dict = {
        'stage_name': stage.stage_name,
        'stage_number': stage.stage_number,
        'version_number': stage.version_number
    }
    
    # Generate PDF
    pdf_generator = PDFVersionHistoryGenerator()
    try:
        pdf_path = pdf_generator.generate_version_history_pdf(
            stage=stage_dict,
            history=history,
            project_name=project.name,
            employee_names=employee_names
        )
        
        # Check if file exists
        if not Path(pdf_path).exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF"
            )
        
        # Return PDF file
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=Path(pdf_path).name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )