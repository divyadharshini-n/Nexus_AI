from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.safety_manual_repository import SafetyManualRepository
from app.db.repositories.code_repository import CodeRepository
from app.db.repositories.stage_repository import StageRepository
from app.schemas.ra_schemas import InterrogateCodeRequest, SafetyAssessmentResponse
from app.core.ra_system.safety_manual_processor import safety_manual_processor
from app.core.ra_system.ra_interrogator import ra_interrogator
from app.config import settings
# from app.core.ra_system.default_safety_checker import default_safety_checker  # Disabled: network issue
# from app.core.ra_system.default_safety_processor import default_safety_processor  # Disabled: network issue loading HuggingFace model
from app.services.version_history_service import VersionHistoryService

router = APIRouter()

@router.post("/safety-check")
async def perform_safety_check(
    request: InterrogateCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform independent safety check using default preloaded manuals
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
    
    # Get generated code
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(stage.id)
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No generated code found for this stage. Please generate code first."
        )
    
    # Prepare code data
    code_data = {
        "program_name": code.program_name,
        "execution_type": code.execution_type,
        "global_labels": code.global_labels or [],
        "local_labels": code.local_labels or [],
        "program_body": code.program_body or ""
    }
    
    # Perform safety check
    try:
        result = await default_safety_checker.check_code_safety(code_data)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Safety check failed')
            )
        
        # Track version history
        version_service = VersionHistoryService(db)
        version_service.create_version_entry(
            code_id=code.id,
            stage_id=stage.id,
            user_id=current_user.id,
            action_type="safety_check",
            metadata={
                "description": "Safety check performed",
                "passed": result['passed'],
                "status": result['status'],
                "risk_level": result['risk_level']
            }
        )
        
        return {
            "success": True,
            "passed": result['passed'],
            "status": result['status'],
            "risk_level": result['risk_level'],
            "compliance_analysis": result['compliance_analysis'],
            "missing_checks": result['missing_checks'],
            "violations": result['violations'],
            "hazards": result['hazards'],
            "required_corrections": result['required_corrections'],
            "recommendations": result['recommendations'],
            "manuals_used": result.get('manuals_used', []),
            "total_manuals": result.get('total_manuals', 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Safety check error: {str(e)}"
        )


@router.get("/default-safety-status")
async def get_default_safety_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check if default safety manuals are loaded
    """
    # is_ready = default_safety_processor.is_default_index_ready()
    is_ready = False  # Disabled temporarily
    
    if not is_ready:
        # Try to get available manuals
        # manuals = default_safety_processor.get_default_manuals()
        manuals = []  # Disabled
        
        return {
            "ready": False,
            "manuals_available": len(manuals),
            "manual_names": [m.name for m in manuals],
            "message": "Default safety manuals found but not processed. Please run setup script."
        }
    
    # Get metadata
    from app.core.ra_system.default_safety_retrieval import default_safety_retrieval
    default_safety_retrieval.load_default_safety_manual()
    metadata = default_safety_retrieval.get_metadata()
    
    return {
        "ready": True,
        "total_manuals": metadata.get('total_manuals', 0),
        "manual_sources": metadata.get('manual_sources', []),
        "total_chunks": metadata.get('total_chunks', 0),
        "word_count": metadata.get('word_count', 0)
    }


@router.post("/process-default-manuals")
async def process_default_manuals(
    current_user: User = Depends(get_current_user)
):
    """
    Process default safety manuals from project folder
    (Admin function - can be restricted)
    """
    try:
        # result = default_safety_processor.process_default_manuals()
        result = {'success': False, 'message': 'Disabled: network issue'}  # Disabled
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to process default safety manuals')
            )
        
        return {
            "success": True,
            "message": "Default safety manuals processed successfully",
            "manuals_processed": result['manuals_processed'],
            "chunks_count": result['chunks_count'],
            "manual_sources": result['manual_sources']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}"
        )

@router.post("/upload-safety-manual")
async def upload_safety_manual(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process safety manual for a project
    """
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
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.docx', '.doc', '.txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, and TXT files are supported"
        )
    
    # Create upload directory
    upload_dir = Path(settings.UPLOADS_PATH) / 'safety_manuals'
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    unique_filename = f"{project_id}_{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Extract text
    try:
        text = safety_manual_processor.extract_text(str(file_path))
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text: {str(e)}"
        )
    
    # Process and create embeddings
    embeddings_dir = Path(settings.EMBEDDINGS_PATH) / 'safety_manuals'
    result = safety_manual_processor.process_and_embed(
        str(file_path),
        str(embeddings_dir),
        project_id
    )
    
    if not result['success']:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get('error', 'Failed to process safety manual')
        )
    
    # Save to database
    safety_repo = SafetyManualRepository(db)
    
    # Delete existing manual for this project
    safety_repo.delete_by_project(project_id)
    
    # Create new record
    manual = safety_repo.create(
        project_id=project_id,
        filename=file.filename,
        file_path=str(file_path),
        content=text[:10000],  # Store first 10k chars
        is_embedded=True
    )
    
    return {
        "success": True,
        "message": "Safety manual uploaded and processed successfully",
        "manual_id": manual.id,
        "chunks_count": result['chunks_count'],
        "word_count": result['word_count']
    }


@router.get("/safety-manual/{project_id}")
async def get_safety_manual_status(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if safety manual exists for a project
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
    
    # Check for safety manual
    safety_repo = SafetyManualRepository(db)
    manual = safety_repo.get_by_project(project_id)
    
    if not manual:
        return {
            "exists": False,
            "message": "No safety manual uploaded"
        }
    
    return {
        "exists": True,
        "filename": manual.filename,
        "uploaded_at": manual.uploaded_at,
        "is_embedded": manual.is_embedded
    }


@router.post("/interrogate", response_model=SafetyAssessmentResponse)
async def interrogate_code(
    request: InterrogateCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Interrogate generated code against safety manual
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
    
    # Check if safety manual exists
    safety_repo = SafetyManualRepository(db)
    manual = safety_repo.get_by_project(stage.project_id)
    
    if not manual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No safety manual uploaded for this project"
        )
    
    # Get generated code
    code_repo = CodeRepository(db)
    code = code_repo.get_by_stage(stage.id)
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No generated code found for this stage"
        )
    
    # Prepare code data
    code_data = {
        "program_name": code.program_name,
        "execution_type": code.execution_type,
        "global_labels": code.global_labels or [],
        "local_labels": code.local_labels or [],
        "program_body": code.program_body or ""
    }
    
    # Interrogate
    embeddings_dir = Path(settings.EMBEDDINGS_PATH) / 'safety_manuals'
    
    try:
        result = await ra_interrogator.interrogate_code(
            stage.project_id,
            code_data,
            str(embeddings_dir)
        )
        
        if not result.get('success'):
            return SafetyAssessmentResponse(
                success=False,
                safe=False,
                status="ERROR",
                severity="UNKNOWN",
                compliance_analysis="",
                hazards=[],
                violations=[],
                required_actions=[],
                recommendations=[],
                error=result.get('error', 'Interrogation failed')
            )
        
        return SafetyAssessmentResponse(
            success=True,
            safe=result['safe'],
            status=result['status'],
            severity=result['severity'],
            compliance_analysis=result['compliance_analysis'],
            hazards=result['hazards'],
            violations=result['violations'],
            required_actions=result['required_actions'],
            recommendations=result['recommendations']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interrogation error: {str(e)}"
        )