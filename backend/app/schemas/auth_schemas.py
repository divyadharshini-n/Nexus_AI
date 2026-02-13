from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime
    
    @field_serializer('role')
    def serialize_role(self, role: str) -> str:
        """Convert role to lowercase for frontend compatibility"""
        return role.lower() if role else 'employee'
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None