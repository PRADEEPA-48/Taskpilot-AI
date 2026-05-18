"""
Calendar routes: fetch upcoming events.
"""
from fastapi import APIRouter, Query
from app.models.schemas import EventsResponse
from app.services.calendar_service import CalendarService
from app.services.oauth_service import get_oauth_service
from app.utils.logger import get_logger

router = APIRouter(tags=["Calendar"])
logger = get_logger(__name__)


@router.get("/events", response_model=EventsResponse, summary="Fetch upcoming calendar events")
async def get_events(days: int = Query(default=7, ge=1, le=30, description="Number of days ahead to fetch")):
    """Return upcoming Google Calendar events for the authenticated user."""
    oauth = get_oauth_service()
    cal = CalendarService(oauth)
    events = await cal.get_upcoming_events(days=days)
    logger.info({"action": "events_fetched", "count": len(events)})
    return EventsResponse(events=events, count=len(events))
