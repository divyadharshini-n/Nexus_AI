from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.file_repository import FileRepository
from app.schemas.input_schemas import FileUploadResponse
from app.core.input_processing.multimodal_handler import multimodal_handler
from app.core.input_processing.input_validator import input_validator
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process file (Word/PDF/TXT/Voice)
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
    
    # Check file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    allowed_extensions = settings.ALLOWED_EXTENSIONS.split(',')
    
    if file_extension[1:] not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Determine file type category
    if file_extension in ['.pdf', '.docx', '.doc', '.txt']:
        file_type_category = 'text'
        upload_dir = Path(settings.UPLOADS_PATH) / 'text'
    elif file_extension in ['.wav', '.mp3']:
        file_type_category = 'voice'
        upload_dir = Path(settings.UPLOADS_PATH) / 'voice'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )
    
    # Create upload directory
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Process file to extract text
    result = multimodal_handler.process_file(str(file_path))
    
    if not result['success']:
        # Delete file if processing failed
        file_path.unlink(missing_ok=True)
        return FileUploadResponse(
            success=False,
            message="Failed to process file",
            error=result.get('error')
        )
    
    # Validate extracted text
    validation = input_validator.validate(result['text'])
    
    if not validation['valid']:
        # Delete file if validation failed
        file_path.unlink(missing_ok=True)
        return FileUploadResponse(
            success=False,
            message="File content validation failed",
            error=validation.get('error')
        )
    
    # Save file record to database
    file_repo = FileRepository(db)
    file_record = file_repo.create(
        project_id=project_id,
        user_id=current_user.id,
        file_type=file_type_category,
        original_filename=file.filename,
        stored_filename=unique_filename,
        file_path=str(file_path),
        file_size=file_size
    )
    
    return FileUploadResponse(
        success=True,
        message="File uploaded and processed successfully",
        file_id=file_record.id,
        extracted_text=result['text'],
        word_count=result['word_count']
    )


@router.get("/files/{project_id}")
async def get_project_files(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all uploaded files for a project"""
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
    
    # Get files
    file_repo = FileRepository(db)
    files = file_repo.get_project_files(project_id)
    
    return {"files": files}


@router.get("/supported-types")
async def get_supported_types():
    """Get list of supported file types"""
    return multimodal_handler.get_supported_types()