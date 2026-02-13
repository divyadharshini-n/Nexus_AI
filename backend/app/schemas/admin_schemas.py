from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CreateEmployeeRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UpdateEmployeeRequest(BaseModel):
    is_active: Optional[bool] = None
    full_name: Optional[str] = None
