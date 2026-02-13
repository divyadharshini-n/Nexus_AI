from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.stage_repository import StageRepository
from app.db.repositories.code_repository import CodeRepository
from app.core.reports.docx_report_generator import docx_report_generator
from app.core.reports.technical_docx_generator_v2 import professional_technical_generator
from app.core.reports.audit_trail_docx_generator import AuditTrailDocumentGenerator
from app.core.reports.audit_trail_pdf_generator import AuditTrailPDFGenerator
from app.core.reports.pdf_report_generator import pdf_report_generator
from app.services.version_history_service import VersionHistoryService

router = APIRouter()


@router.get("/docx/{project_id}")
async def generate_docx_report(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate comprehensive technical documentation report for a project
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
    
    # Get stages
    stage_repo = StageRepository(db)
    stages = stage_repo.get_by_project(project_id)
    
    if not stages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stages found for this project"
        )
    
    # Check if any stage has generated code
    has_generated_code = False
    for stage in stages:
        code_repo = CodeRepository(db)
        stage_codes = code_repo.get_by_stage(stage.id)
        if stage_codes:
            has_generated_code = True
            break
    
    if not has_generated_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No generated code found. Please generate code before creating report."
        )
    
    # Get generated codes
    codes = code_repo.get_project_codes(project_id)
    
    # Get project owner/admin information
    owner_name = current_user.full_name or current_user.username
    
    # Prepare data
    project_data = {
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
        "code": f"PRJ-{project_id:04d}",
        "client": "N/A",
        "location": "N/A"
    }
    
    stages_data = [
        {
            "id": s.id,
            "stage_number": s.stage_number,
            "name": s.stage_name,
            "stage_type": s.stage_type,
            "description": s.description,
            "original_logic": s.original_logic,
            "edited_logic": s.edited_logic,
            "is_validated": s.is_validated,
            "is_finalized": s.is_finalized,
            "version_number": s.version_number,
            "last_action": s.last_action,
            "last_action_timestamp": s.last_action_timestamp
        }
        for s in stages
    ]
    
    codes_data = [
        {
            "stage_id": c.stage_id,
            "block_name": c.program_name,
            "program_name": c.program_name,
            "execution_type": c.execution_type,
            "global_labels": c.global_labels or [],
            "local_labels": c.local_labels or [],
            "program_body": c.program_body or ""
        }
        for c in codes
    ]
    
    # Generate professional technical documentation report
    try:
        report_path = professional_technical_generator.generate_technical_report(
            project=project_data,
            stages=stages_data,
            codes=codes_data,
            admin_name=owner_name,
            validations=None
        )
        
        # Return file
        return FileResponse(
            path=report_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=Path(report_path).name
        )
        
    except Exception as e:
        import traceback
        print(f"Report generation error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}"
        )


@router.get("/audit-trail/{project_id}")
async def generate_audit_trail_report(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate comprehensive version history & audit trail report for a project
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
            detail="Not authorized to access this project"
        )
    
    try:
        # Get project data
        stage_repo = StageRepository(db)
        code_repo = CodeRepository(db)
        
        stages = stage_repo.get_project_stages(project_id)
        
        # Get generated codes
        codes = {}
        for stage in stages:
            code = code_repo.get_by_stage(stage.id)
            codes[stage.id] = code.program_body if code else None
        
        # Prepare project data dictionary
        project_data = {
            'id': project.id,
            'name': project.name,
            'code': f"PRJ-{project.id:04d}",
            'client': 'Client Organization',  # Add to model if needed
            'location': 'Project Location',    # Add to model if needed
            'control_logic': project.description or '',
            'created_at': project.created_at.strftime("%d-%m-%Y %H:%M:%S") if project.created_at else 'N/A',
            'updated_at': project.updated_at.strftime("%d-%m-%Y %H:%M:%S") if project.updated_at else 'N/A',
            'status': 'Active',
            'duration_days': (project.updated_at - project.created_at).days if project.created_at and project.updated_at else 0,
            'generation_count': len([c for c in codes.values() if c]),
            'revision_count': 1,
            'admin_id': current_user.id,
            'admin_name': current_user.username,
            'admin_email': current_user.email
        }
        
        # Prepare stages data
        stages_data = []
        for stage in stages:
            stages_data.append({
                'id': stage.id,
                'name': stage.stage_name,
                'description': stage.description or '',
                'order': stage.stage_number
            })
        
        # Generate audit trail report
        generator = AuditTrailPDFGenerator()
        output_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'reports'
        
        report_path = generator.generate_audit_trail_report(
            project=project_data,
            stages=stages_data,
            codes=codes,
            admin_name=current_user.username,
            output_path=str(output_dir)
        )
        
        # Return file
        return FileResponse(
            path=report_path,
            media_type='application/pdf',
            filename=Path(report_path).name
        )
        
    except Exception as e:
        import traceback
        print(f"Audit trail report generation error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit trail report generation error: {str(e)}"
        )


@router.get("/pdf/{project_id}")
async def generate_pdf_report(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF report for a project
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
    
    # Get stages
    stage_repo = StageRepository(db)
    stages = stage_repo.get_by_project(project_id)
    
    if not stages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stages found for this project"
        )
    
    # Get generated codes
    code_repo = CodeRepository(db)
    codes = code_repo.get_project_codes(project_id)
    
    # Get version history service
    version_service = VersionHistoryService(db)
    
    # Prepare data
    project_data = {
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at
    }
    
    stages_data = [
        {
            "stage_number": s.stage_number,
            "stage_name": s.stage_name,
            "stage_type": s.stage_type,
            "description": s.description,
            "original_logic": s.original_logic,
            "edited_logic": s.edited_logic,
            "is_validated": s.is_validated,
            "is_finalized": s.is_finalized,
            "version_number": s.version_number,
            "last_action": s.last_action,
            "last_action_timestamp": s.last_action_timestamp
        }
        for s in stages
    ]
    
    codes_data = [
        {
            "program_name": c.program_name,
            "execution_type": c.execution_type,
            "global_labels": c.global_labels or [],
            "local_labels": c.local_labels or [],
            "program_body": c.program_body or ""
        }
        for c in codes
    ]
    
    # Generate report
    try:
        report_path = pdf_report_generator.generate_project_report(
            project=project_data,
            stages=stages_data,
            codes=codes_data
        )
        
        # Return file
        return FileResponse(
            path=report_path,
            media_type="application/pdf",
            filename=Path(report_path).name
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}"
        )


@router.get("/summary/{project_id}")
async def get_report_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get report summary data
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
    
    # Get stages
    stage_repo = StageRepository(db)
    stages = stage_repo.get_by_project(project_id)
    
    # Get codes
    code_repo = CodeRepository(db)
    codes = code_repo.get_project_codes(project_id)
    
    # Calculate statistics
    validated_count = sum(1 for s in stages if s.is_validated)
    finalized_count = sum(1 for s in stages if s.is_finalized)
    
    return {
        "project_name": project.name,
        "total_stages": len(stages),
        "total_codes": len(codes),
        "validated_stages": validated_count,
        "finalized_stages": finalized_count,
        "completion_percentage": (finalized_count / len(stages) * 100) if stages else 0
    }