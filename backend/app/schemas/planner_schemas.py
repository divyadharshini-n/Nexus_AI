from pydantic import BaseModel
from typing import List, Dict, Optional


class CreatePlanRequest(BaseModel):
    project_id: int
    control_logic: str


class StageInfo(BaseModel):
    stage_number: int
    stage_name: str
    stage_type: str
    description: str
    original_logic: str


class DependencyInfo(BaseModel):
    from_stage: int
    to_stage: int
    condition: str


class CreatePlanResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    analysis: Optional[Dict] = None
    stages: Optional[List[StageInfo]] = None
    dependencies: Optional[List[DependencyInfo]] = None
    dependency_validation: Optional[Dict] = None
    transition_graph: Optional[Dict] = None
    total_stages: Optional[int] = None