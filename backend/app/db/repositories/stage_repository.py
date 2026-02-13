from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.stage import Stage


class StageRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        project_id: int,
        stage_number: int,
        stage_name: str,
        stage_type: str,
        description: str,
        original_logic: str,
        dependencies: dict = None,
        entry_conditions: dict = None,
        exit_conditions: dict = None
    ) -> Stage:
        """Create a new stage"""
        stage = Stage(
            project_id=project_id,
            stage_number=stage_number,
            stage_name=stage_name,
            stage_type=stage_type,
            description=description,
            original_logic=original_logic,
            dependencies=dependencies,
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions
        )
        self.db.add(stage)
        self.db.commit()
        self.db.refresh(stage)
        return stage
    
    def get_project_stages(self, project_id: int) -> List[Stage]:
        """Get all stages for a project"""
        return self.db.query(Stage).filter(
            Stage.project_id == project_id
        ).order_by(Stage.stage_number).all()
    
    def get_by_id(self, stage_id: int) -> Optional[Stage]:
        """Get stage by ID"""
        return self.db.query(Stage).filter(Stage.id == stage_id).first()
    
    def update_logic(self, stage_id: int, edited_logic: str):
        """Update stage logic"""
        stage = self.get_by_id(stage_id)
        if stage:
            stage.edited_logic = edited_logic
            self.db.commit()
    
    def mark_validated(self, stage_id: int):
        """Mark stage as validated"""
        stage = self.get_by_id(stage_id)
        if stage:
            stage.is_validated = True
            self.db.commit()
    
    def mark_finalized(self, stage_id: int):
        """Mark stage as finalized"""
        stage = self.get_by_id(stage_id)
        if stage:
            stage.is_finalized = True
            self.db.commit()
    
    def delete_project_stages(self, project_id: int):
        """Delete all stages for a project"""
        self.db.query(Stage).filter(Stage.project_id == project_id).delete()
        self.db.commit()
    
    def get_by_project(self, project_id: int):
        return (
            self.db.query(Stage)
            .filter(Stage.project_id == project_id)
            .order_by(Stage.stage_number)
            .all()
        )