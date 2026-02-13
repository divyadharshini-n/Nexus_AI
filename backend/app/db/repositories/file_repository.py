from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.uploaded_file import UploadedFile, FileType


class FileRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        project_id: int,
        user_id: int,
        file_type: str,
        original_filename: str,
        stored_filename: str,
        file_path: str,
        file_size: int
    ) -> UploadedFile:
        """Create file record"""
        file_record = UploadedFile(
            project_id=project_id,
            user_id=user_id,
            file_type=FileType(file_type),
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size
        )
        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        return file_record
    
    def get_project_files(self, project_id: int) -> List[UploadedFile]:
        """Get all files for a project"""
        return self.db.query(UploadedFile).filter(
            UploadedFile.project_id == project_id
        ).order_by(UploadedFile.uploaded_at.desc()).all()
    
    def get_by_id(self, file_id: int) -> Optional[UploadedFile]:
        """Get file by ID"""
        return self.db.query(UploadedFile).filter(UploadedFile.id == file_id).first()