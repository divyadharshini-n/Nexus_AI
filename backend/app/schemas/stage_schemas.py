from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class UpdateStageLogicRequest(BaseModel):
    stage_id: int
    edited_logic: str


class ValidateStageRequest(BaseModel):
    stage_id: int


class FinalizeStageRequest(BaseModel):
    stage_id: int


class ValidationIssue(BaseModel):
    severity: str  # 'critical', 'moderate', 'optional'
    title: str
    description: str
    recommended_logic: str


class ValidationResponse(BaseModel):
    success: bool
    valid: bool
    status: str
    semantic_analysis: str
    logical_consistency: str
    safety_compliance: str
    issues: List[str]  # Original simple string issues
    recommendations: List[str]  # Original simple string recommendations
    categorized_issues: Optional[List[ValidationIssue]] = []  # New severity-based issues
    error: Optional[str] = None