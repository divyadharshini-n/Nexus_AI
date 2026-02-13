from pydantic import BaseModel
from typing import Optional


class AIDudeQueryRequest(BaseModel):
    question: str
    project_id: int
    code_context: Optional[str] = None


class AIDudeQueryResponse(BaseModel):
    answer: str
    manual_grounded: bool