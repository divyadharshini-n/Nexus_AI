from pydantic import BaseModel
from typing import List, Optional


class InterrogateCodeRequest(BaseModel):
    stage_id: int


class SafetyAssessmentResponse(BaseModel):
    success: bool
    safe: bool
    status: str
    severity: str
    compliance_analysis: str
    hazards: List[str]
    violations: List[str]
    required_actions: List[str]
    recommendations: List[str]
    error: Optional[str] = None