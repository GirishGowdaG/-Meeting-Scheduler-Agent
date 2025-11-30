"""
Meeting Schemas
Pydantic models for meeting data validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.schemas.intent import ParticipantSchema
from app.schemas.slot import SlotSchema


class MeetingBase(BaseModel):
    """Base meeting schema"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    participants: List[ParticipantSchema] = Field(default_factory=list)
    duration_minutes: int = Field(..., gt=0)
    timezone: str


class MeetingCreate(MeetingBase):
    """Schema for creating a meeting"""
    user_id: UUID
    status: str = "proposed"


class MeetingUpdate(BaseModel):
    """Schema for updating a meeting"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_id: Optional[str] = None
    status: Optional[str] = None


class MeetingSchema(MeetingBase):
    """Schema for meeting response"""
    id: UUID
    user_id: UUID
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Sync meeting",
                "description": "Quick catch-up",
                "participants": [
                    {"email": "alice@example.com", "name": "Alice"}
                ],
                "duration_minutes": 30,
                "start_time": "2024-01-15T14:00:00+00:00",
                "end_time": "2024-01-15T14:30:00+00:00",
                "timezone": "America/New_York",
                "event_id": "abc123",
                "status": "confirmed",
                "created_at": "2024-01-14T10:00:00+00:00",
                "updated_at": "2024-01-14T10:05:00+00:00"
            }
        }


class CreateEventRequest(BaseModel):
    """Request schema for creating a calendar event"""
    slot: SlotSchema
    title: str
    description: Optional[str] = None
    participants: List[ParticipantSchema] = Field(default_factory=list)
    meeting_id: Optional[UUID] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "slot": {
                    "start": "2024-01-15T14:00:00+00:00",
                    "end": "2024-01-15T14:30:00+00:00",
                    "score": 0.95,
                    "conflicts": []
                },
                "title": "Sync meeting",
                "description": "Quick catch-up",
                "participants": [
                    {"email": "alice@example.com", "name": "Alice"}
                ]
            }
        }


class CreateEventResponse(BaseModel):
    """Response schema for created event"""
    event_id: str
    calendar_link: str
    meeting_id: UUID
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "abc123xyz",
                "calendar_link": "https://calendar.google.com/calendar/event?eid=abc123xyz",
                "meeting_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
