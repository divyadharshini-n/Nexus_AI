from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ShareProjectRequest(BaseModel):
    user_id: int


class UnshareProjectRequest(BaseModel):
    user_id: int


class SharedUserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: str
    
    class Config:
        from_attributes = True


class ProjectShareResponse(BaseModel):
    id: int
    project_id: int
    shared_with: SharedUserResponse
    shared_at: datetime
    
    class Config:
        from_attributes = True
