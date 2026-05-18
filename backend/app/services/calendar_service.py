"""
Google Calendar service.
Creates events, adds reminders, and fetches upcoming events.
"""
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import HTTPException
from app.models.schemas import ExtractedTask, CalendarEvent
from app.services.oauth_service import OAuthService
from app.utils.helpers import parse_natural_date
from app.utils.logger import get_logger

logger = get_logger(__name__)

REMINDER_METHODS = {"email": "email", "popup": "popup"}


class CalendarService:
    def __init__(self, oauth: OAuthService):
        self.oauth = oauth

    def _get_service(self):
        creds = self.oauth.get_credentials()
        if not creds:
            raise HTTPException(status_code=401, detail="Not authenticated. Please complete Google OAuth.")
        return build("calendar", "v3", credentials=creds)

    async def create_event(self, task: ExtractedTask) -> dict:
        """Create a Google Calendar event from an extracted task."""
        try:
            service = self._get_service()
            start_dt, end_dt = parse_natural_date(task.date, task.time)

            reminder_method = REMINDER_METHODS.get(task.notify, "email")
            event_body = {
                "summary": task.title,
                "description": f"Type: {task.type}\nCreated by TaskPilot AI",
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "UTC",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": reminder_method, "minutes": 30},
                        {"method": "popup", "minutes": 10},
                    ],
                },
            }

            created = service.events().insert(calendarId="primary", body=event_body).execute()
            logger.info({"action": "calendar_create", "event_id": created.get("id")})
            return created

        except HttpError as e:
            logger.error({"action": "calendar_create_error", "error": str(e)})
            raise HTTPException(status_code=502, detail=f"Google Calendar API error: {e}")

    async def get_upcoming_events(self, days: int = 7) -> list[CalendarEvent]:
        """Fetch upcoming events within the next N days."""
        try:
            service = self._get_service()
            now = datetime.now(timezone.utc)
            time_max = now + timedelta(days=days)

            result = service.events().list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
                maxResults=50,
            ).execute()

            items = result.get("items", [])
            events = []
            for item in items:
                start = item.get("start", {})
                end = item.get("end", {})
                events.append(CalendarEvent(
                    id=item.get("id", ""),
                    title=item.get("summary", "No Title"),
                    start=start.get("dateTime", start.get("date", "")),
                    end=end.get("dateTime", end.get("date", "")),
                    description=item.get("description"),
                    html_link=item.get("htmlLink"),
                ))

            logger.info({"action": "calendar_fetch", "count": len(events)})
            return events

        except HttpError as e:
            logger.error({"action": "calendar_fetch_error", "error": str(e)})
            raise HTTPException(status_code=502, detail=f"Google Calendar API error: {e}")


def get_calendar_service(oauth: OAuthService) -> CalendarService:
    return CalendarService(oauth)
