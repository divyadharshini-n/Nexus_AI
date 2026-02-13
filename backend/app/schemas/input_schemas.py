from pydantic import BaseModel
from typing import Optional


class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[int] = None
    extracted_text: Optional[str] = None
    word_count: Optional[int] = None
    error: Optional[str] = None


class ProcessFileRequest(BaseModel):
    file_id: int
    project_id: int