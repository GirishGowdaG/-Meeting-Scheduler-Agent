"""
Slot Schemas
Pydantic models for time slot proposals
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from uuid import UUID

from app.schemas.intent import ParticipantSchema, TimeWindowSchema


from typing import Union

class SlotSchema(BaseModel):
    """Schema for a proposed time slot"""
    start: Union[datetime, str]
    end: Union[datetime, str]
    score: float = Field(..., ge=0.0, le=1.0)
    conflicts: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "start": "2024-01-15T14:00:00+00:00",
                "end": "2024-01-15T14:30:00+00:00",
                "score": 0.95,
                "conflicts": []
            }
        }


class ProposeSlotsRequest(BaseModel):
    """Request schema for proposing time slots"""
    participants: List[ParticipantSchema]
    duration_minutes: int = Field(..., gt=0)
    preferred_windows: List[TimeWindowSchema]
    
    class Config:
        json_schema_extra = {
            "example": {
                "participants": [
                    {"email": "alice@example.com", "name": "Alice"}
                ],
                "duration_minutes": 30,
                "preferred_windows": [
                    {
                        "start": "2024-01-15T09:00:00+00:00",
                        "end": "2024-01-15T18:00:00+00:00"
                    }
                ]
            }
        }


class ProposeSlotsResponse(BaseModel):
    """Response schema for proposed slots"""
    slots: List[SlotSchema] = Field(..., min_length=0, max_length=3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "slots": [
                    {
                        "start": "2024-01-15T14:00:00+00:00",
                        "end": "2024-01-15T14:30:00+00:00",
                        "score": 0.95,
                        "conflicts": []
                    }
                ]
            }
        }
