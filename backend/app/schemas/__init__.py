"""Pydantic Schemas Package"""
from app.schemas.user import UserSchema, UserCreate
from app.schemas.intent import (
    ParticipantSchema,
    TimeWindowSchema,
    IntentSchema,
    ParseIntentRequest,
    ParseIntentResponse
)
from app.schemas.slot import SlotSchema, ProposeSlotsRequest, ProposeSlotsResponse
from app.schemas.meeting import (
    MeetingSchema,
    MeetingCreate,
    MeetingUpdate,
    CreateEventRequest,
    CreateEventResponse
)

__all__ = [
    "UserSchema",
    "UserCreate",
    "ParticipantSchema",
    "TimeWindowSchema",
    "IntentSchema",
    "ParseIntentRequest",
    "ParseIntentResponse",
    "SlotSchema",
    "ProposeSlotsRequest",
    "ProposeSlotsResponse",
    "MeetingSchema",
    "MeetingCreate",
    "MeetingUpdate",
    "CreateEventRequest",
    "CreateEventResponse",
]
