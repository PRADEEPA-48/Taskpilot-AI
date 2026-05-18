from pydantic import BaseModel
from typing import List, Optional


class UserInput(BaseModel):
    text: str


class AgentResponse(BaseModel):
    intent: str = ""
    title: str = ""
    date: str = ""
    time: str = ""
    attendees: List[str] = []
    notification: str = ""
    actions: List[str] = []
    message: str = ""
    alternative_slot: str = ""
    busy_slots: List[str] = []
    reminder_time: str = ""
    priority_order: List[str] = []
    agenda: List[str] = []
