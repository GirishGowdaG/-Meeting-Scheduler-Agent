"""
User Schemas
Pydantic models for user data validation
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserSchema(UserBase):
    """Schema for user response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
