from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.db.models.generated_code import GeneratedCode
import json


class CodeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        project_id: int,
        stage_id: Optional[int],
        global_labels: List[Dict],
        local_labels: List[Dict],
        program_body: str,
        program_name: str,
        execution_type: str,
        metadata: Dict = None,
        program_blocks: List[Dict] = None,
        functions: List[Dict] = None,
        function_blocks: List[Dict] = None
    ) -> GeneratedCode:
        """Create generated code record"""
        code = GeneratedCode(
            project_id=project_id,
            stage_id=stage_id,
            global_labels=global_labels,
            local_labels=local_labels,
            program_body=program_body,
            program_name=program_name,
            execution_type=execution_type,
            code_metadata=metadata,
            program_blocks=program_blocks or [],
            functions=functions or [],
            function_blocks=function_blocks or []
        )
        self.db.add(code)
        self.db.commit()
        self.db.refresh(code)
        return code
    
    def get_by_stage(self, stage_id: int) -> Optional[GeneratedCode]:
        """Get code for a specific stage"""
        return self.db.query(GeneratedCode).filter(
            GeneratedCode.stage_id == stage_id
        ).order_by(GeneratedCode.created_at.desc()).first()
    
    def get_project_codes(self, project_id: int) -> List[GeneratedCode]:
        """Get all generated code for a project"""
        return self.db.query(GeneratedCode).filter(
            GeneratedCode.project_id == project_id
        ).order_by(GeneratedCode.created_at.desc()).all()
    
    def delete_by_stage(self, stage_id: int):
        """Delete code for a stage"""
        self.db.query(GeneratedCode).filter(
            GeneratedCode.stage_id == stage_id
        ).delete()
        self.db.commit()