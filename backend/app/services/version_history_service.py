from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import Optional, Dict, Any, List
import difflib
from app.db.models.version_history import VersionHistory, VersionLevel
from app.db.models.stage import Stage
from app.db.models.generated_code import GeneratedCode
from app.db.models.user import User


class VersionHistoryService:
    """Service for managing version history tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def increment_version(self, current_version: str, action_type: str) -> str:
        """
        Increment version number based on action type
        - edit_logic: increment patch (1.0.0 -> 1.0.1)
        - validate: increment minor (1.0.0 -> 1.1.0)
        - generate_code: increment minor (1.0.0 -> 1.1.0)
        - safety_check: increment patch (1.0.0 -> 1.0.1)
        """
        try:
            parts = current_version.split('.')
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            if action_type in ['validate', 'generate_code']:
                minor += 1
                patch = 0
            elif action_type in ['edit_logic', 'safety_check']:
                patch += 1
            
            return f"{major}.{minor}.{patch}"
        except:
            return "1.0.0"
    
    def _generate_diff(self, old_text: str, new_text: str) -> str:
        """Generate a unified diff between old and new text"""
        if not old_text and not new_text:
            return ""
        
        old_lines = (old_text or "").splitlines(keepends=True)
        new_lines = (new_text or "").splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=3
        )
        
        return ''.join(diff)
    
    def create_version_entry(
        self,
        code_id: int,
        stage_id: int,
        user_id: int,
        action_type: str,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> VersionHistory:
        """Create a new version history entry with proper diff tracking"""
        
        # Get current stage version
        stage = self.db.query(Stage).filter(Stage.id == stage_id).first()
        old_version = stage.version_number if stage else "1.0.0"
        new_version = self.increment_version(old_version, action_type)
        
        # Count validations for this stage - simplified query
        try:
            validation_count = self.db.query(VersionHistory).filter(
                VersionHistory.stage_id == stage_id
            ).count()
        except:
            validation_count = 0
        
        # Update stage version
        if stage:
            stage.version_number = new_version
            stage.last_action = action_type
            stage.last_action_timestamp = datetime.utcnow()
        
        # Extract text content for diff
        old_text = ""
        new_text = ""
        
        if action_type == 'edit_logic':
            old_text = old_data.get('edited_logic', '') if old_data else ''
            new_text = new_data.get('edited_logic', '') if new_data else ''
        elif action_type == 'generate_code':
            old_text = old_data.get('program_body', '') if old_data else ''
            new_text = new_data.get('program_body', '') if new_data else ''
        
        # Generate diff
        diff_text = self._generate_diff(old_text, new_text)
        
        # Create version history entry
        version_entry = VersionHistory(
            code_id=code_id,
            stage_id=stage_id,
            user_id=user_id,
            level=VersionLevel.EVENT,
            version_number=new_version,
            old_code=old_text,
            new_code=new_text,
            diff=diff_text,
            timestamp=datetime.utcnow(),
            version_metadata={
                "action": action_type,
                "previous_version": old_version,
                "new_version": new_version,
                "validation_count": validation_count,
                **(metadata or {})
            }
        )
        
        self.db.add(version_entry)
        self.db.commit()
        self.db.refresh(version_entry)
        
        return version_entry
    
    def get_stage_version_history(self, stage_id: int):
        """Get all version history for a stage with employee names"""
        return (
            self.db.query(VersionHistory)
            .options(joinedload(VersionHistory.user))
            .filter(VersionHistory.stage_id == stage_id)
            .order_by(VersionHistory.timestamp.desc())
            .all()
        )
    
    def get_stage_version_history_with_employees(self, stage_id: int) -> List[Dict[str, Any]]:
        """Get version history with employee details"""
        versions = (
            self.db.query(VersionHistory, User.full_name, User.username)
            .join(User, VersionHistory.user_id == User.id)
            .filter(VersionHistory.stage_id == stage_id)
            .order_by(VersionHistory.timestamp.desc())
            .all()
        )
        
        result = []
        for version, full_name, username in versions:
            result.append({
                "id": version.id,
                "version_number": version.version_number,
                "old_code": version.old_code,
                "new_code": version.new_code,
                "diff": version.diff,
                "timestamp": version.timestamp,
                "user_id": version.user_id,
                "employee_name": full_name or username,
                "version_metadata": version.version_metadata
            })
        
        return result
    
    def get_latest_version(self, stage_id: int) -> Optional[str]:
        """Get the latest version number for a stage"""
        stage = self.db.query(Stage).filter(Stage.id == stage_id).first()
        return stage.version_number if stage else None
    
    def get_version_by_number(self, stage_id: int, version_number: str) -> Optional[VersionHistory]:
        """Get a specific version entry by version number"""
        return (
            self.db.query(VersionHistory)
            .filter(
                VersionHistory.stage_id == stage_id,
                VersionHistory.version_number == version_number
            )
            .first()
        )
    
    def get_version_summary(self, stage_id: int) -> Dict[str, Any]:
        """Get version summary for a stage"""
        stage = self.db.query(Stage).filter(Stage.id == stage_id).first()
        history = self.get_stage_version_history(stage_id)
        
        return {
            "current_version": stage.version_number if stage else "1.0.0",
            "last_action": stage.last_action if stage else None,
            "last_updated": stage.last_action_timestamp.isoformat() if stage and stage.last_action_timestamp else None,
            "total_versions": len(history),
            "history": [
                {
                    "version": v.version_number,
                    "action": v.version_metadata.get("action") if v.version_metadata else None,
                    "timestamp": v.timestamp.isoformat(),
                    "metadata": v.version_metadata
                }
                for v in history[:10]  # Last 10 versions
            ]
        }
