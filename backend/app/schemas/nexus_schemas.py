from pydantic import BaseModel
from typing import Optional, Dict


class NexusChatRequest(BaseModel):
    message: str
    project_id: int


class NexusChatResponse(BaseModel):
    response: str
    phase: str
    manual_context_used: bool