"""
Global Labels Service
Manages project-wide global labels that are shared across all stages
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.models.generated_code import GeneratedCode
from app.db.models.project import Project
import logging

logger = logging.getLogger(__name__)


class GlobalLabelsService:
    """Service for managing project-wide global labels"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_project_global_labels(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all global labels for a project by aggregating from all stages
        """
        # Get all generated codes for this project
        codes = self.db.query(GeneratedCode).filter(
            GeneratedCode.project_id == project_id,
            GeneratedCode.stage_id.isnot(None)  # Only stage-specific codes
        ).all()
        
        # Collect all global labels
        all_labels = []
        seen_devices = set()
        seen_names = set()
        
        for code in codes:
            if code.global_labels:
                for label in code.global_labels:
                    label_name = label.get('name', '')
                    label_device = label.get('device', '')
                    
                    # Use device as primary key, name as secondary
                    identifier = label_device if label_device else label_name
                    
                    if identifier and identifier not in seen_devices:
                        all_labels.append(label)
                        seen_devices.add(identifier)
                        if label_name:
                            seen_names.add(label_name)
        
        logger.info(f"Retrieved {len(all_labels)} unique global labels for project {project_id}")
        return all_labels
    
    def merge_global_labels(
        self, 
        existing_labels: List[Dict[str, Any]], 
        new_labels: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge new global labels with existing ones, avoiding duplicates
        """
        merged = list(existing_labels)
        existing_devices = {label.get('device', '') for label in existing_labels if label.get('device')}
        existing_names = {label.get('name', '') for label in existing_labels if label.get('name')}
        
        for new_label in new_labels:
            label_name = new_label.get('name', '')
            label_device = new_label.get('device', '')
            
            # Check if this label already exists
            identifier = label_device if label_device else label_name
            
            if identifier and identifier not in existing_devices and label_name not in existing_names:
                merged.append(new_label)
                if label_device:
                    existing_devices.add(label_device)
                if label_name:
                    existing_names.add(label_name)
                logger.debug(f"Added new global label: {label_name or label_device}")
        
        logger.info(f"Merged labels: {len(existing_labels)} existing + {len(new_labels)} new = {len(merged)} total")
        return merged
    
    def update_all_stages_with_global_labels(
        self, 
        project_id: int, 
        global_labels: List[Dict[str, Any]]
    ):
        """
        Update all stages in a project to use the unified global labels
        """
        codes = self.db.query(GeneratedCode).filter(
            GeneratedCode.project_id == project_id,
            GeneratedCode.stage_id.isnot(None)
        ).all()
        
        updated_count = 0
        for code in codes:
            code.global_labels = global_labels
            updated_count += 1
        
        if updated_count > 0:
            self.db.commit()
            logger.info(f"Updated {updated_count} stages with unified global labels")
        
        return updated_count
    
    def ensure_common_global_labels(self, project_id: int):
        """
        Ensure all stages in a project share the same global labels
        This should be called after generating code for any stage
        """
        # Get all unique global labels across the project
        all_global_labels = self.get_project_global_labels(project_id)
        
        # Update all stages to use these labels
        self.update_all_stages_with_global_labels(project_id, all_global_labels)
        
        return all_global_labels


# Create a singleton getter
def get_global_labels_service(db: Session) -> GlobalLabelsService:
    return GlobalLabelsService(db)
