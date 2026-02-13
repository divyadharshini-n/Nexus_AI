from pydantic import BaseModel
from typing import List, Dict, Optional


class GenerateCodeRequest(BaseModel):
    stage_id: int


class LabelInfo(BaseModel):
    name: str
    data_type: str
    class_type: str = ""
    device: str = ""
    initial_value: str = ""
    comment: str = ""


class GeneratedCodeResponse(BaseModel):
    success: bool
    stage_id: int
    stage_name: str
    global_labels: List[Dict]
    local_labels: List[Dict]
    program_body: str
    metadata: Dict
    error: Optional[str] = None
    program_blocks: Optional[List[Dict]] = []
    functions: Optional[List[Dict]] = []
    function_blocks: Optional[List[Dict]] = []


class UpdateCodeRequest(BaseModel):
    stage_id: int
    program_body: str
    global_labels: Optional[List[Dict]] = None
    local_labels: Optional[List[Dict]] = None


class UpdateCodeResponse(BaseModel):
    success: bool
    message: str
    stage_id: int
    error: Optional[str] = None
