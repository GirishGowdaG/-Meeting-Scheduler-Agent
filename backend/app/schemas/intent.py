"""
Intent Extraction Schemas
Pydantic models for natural language intent parsing
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional


class ParticipantSchema(BaseModel):
    """Schema for meeting participant"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "alice@example.com",
                "name": "Alice Smith"
            }
        }


class TimeWindowSchema(BaseModel):
    """Schema for preferred time window"""
    start: datetime
    end: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "start": "2024-01-15T09:00:00+00:00",
                "end": "2024-01-15T18:00:00+00:00"
            }
        }


class IntentSchema(BaseModel):
    """Schema for extracted meeting intent"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    participants: List[ParticipantSchema] = Field(default_factory=list)
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours
    preferred_windows: List[TimeWindowSchema] = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sync meeting with Alice",
                "description": "Quick catch-up on project status",
                "participants": [
                    {"email": "alice@example.com", "name": "Alice"}
                ],
                "duration_minutes": 30,
                "preferred_windows": [
                    {
                        "start": "2024-01-15T14:00:00+00:00",
                        "end": "2024-01-15T18:00:00+00:00"
                    }
                ]
            }
        }


class ParseIntentRequest(BaseModel):
    """Request schema for intent parsing"""
    prompt: str = Field(..., min_length=1, max_length=1000)
    user_timezone: str = Field(default="UTC")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Schedule a 30-minute sync with alice@example.com tomorrow afternoon",
                "user_timezone": "America/New_York"
            }
        }


class ParseIntentResponse(IntentSchema):
    """Response schema for intent parsing"""
    pass
