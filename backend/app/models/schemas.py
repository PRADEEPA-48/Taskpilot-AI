"""
Pydantic models for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ── Requests ──────────────────────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Natural language task description")
    user_email: Optional[str] = Field(None, description="User email for notifications")


class VoiceInput(BaseModel):
    text: str = Field(..., min_length=1, description="Speech-to-text converted string")
    user_email: Optional[str] = None


# ── AI Extraction ─────────────────────────────────────────────────────────────

class ExtractedTask(BaseModel):
    title: str
    date: str
    time: str
    type: str = Field(..., description="meeting | task")
    notify: str = Field(..., description="email | popup | none")


# ── Calendar ──────────────────────────────────────────────────────────────────

class CalendarEvent(BaseModel):
    id: str
    title: str
    start: str
    end: str
    description: Optional[str] = None
    html_link: Optional[str] = None


# ── Responses ─────────────────────────────────────────────────────────────────

class ProcessResponse(BaseModel):
    success: bool
    task: ExtractedTask
    event_id: Optional[str] = None
    event_link: Optional[str] = None
    notification_sent: bool = False
    message: str = ""


class EventsResponse(BaseModel):
    events: list[CalendarEvent]
    count: int


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
