from sqlalchemy.orm import Session
from typing import Optional
from app.db.models.safety_manual import SafetyManual


class SafetyManualRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        project_id: int,
        filename: str,
        file_path: str,
        content: str,
        is_embedded: bool = False
    ) -> SafetyManual:
        """Create safety manual record"""
        manual = SafetyManual(
            project_id=project_id,
            filename=filename,
            file_path=file_path,
            content=content,
            is_embedded=is_embedded
        )
        self.db.add(manual)
        self.db.commit()
        self.db.refresh(manual)
        return manual
    
    def get_by_project(self, project_id: int) -> Optional[SafetyManual]:
        """Get safety manual for a project"""
        return self.db.query(SafetyManual).filter(
            SafetyManual.project_id == project_id
        ).first()
    
    def mark_embedded(self, manual_id: int):
        """Mark manual as embedded"""
        manual = self.db.query(SafetyManual).filter(SafetyManual.id == manual_id).first()
        if manual:
            manual.is_embedded = True
            self.db.commit()
    
    def delete_by_project(self, project_id: int):
        """Delete safety manual for a project"""
        self.db.query(SafetyManual).filter(
            SafetyManual.project_id == project_id
        ).delete()
        self.db.commit()