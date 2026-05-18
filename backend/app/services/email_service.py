"""
Email notification service.
Supports Resend (default) and Gmail API as providers.
Selected via EMAIL_PROVIDER env variable.
"""
import base64
from email.mime.text import MIMEText
from app.config.settings import get_settings
from app.models.schemas import ExtractedTask
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _build_email_body(task: ExtractedTask, event_link: str | None) -> str:
    link_line = f"\n\nCalendar Link: {event_link}" if event_link else ""
    return f"""\
Hi there,

Your {task.type} has been scheduled successfully via TaskPilot AI.

Details:
  Title   : {task.title}
  Date    : {task.date}
  Time    : {task.time}
  Type    : {task.type}
  Reminder: {task.notify}
{link_line}

— TaskPilot AI
"""


async def send_via_resend(
    to_email: str,
    task: ExtractedTask,
    event_link: str | None,
) -> bool:
    """Send email using Resend API."""
    try:
        import resend  # type: ignore

        settings = get_settings()
        resend.api_key = settings.resend_api_key

        resend.Emails.send({
            "from": settings.sender_email,
            "to": to_email,
            "subject": f"TaskPilot AI: {task.title} scheduled",
            "text": _build_email_body(task, event_link),
        })
        logger.info({"action": "email_sent", "provider": "resend", "to": to_email})
        return True
    except Exception as e:
        logger.error({"action": "email_error", "provider": "resend", "error": str(e)})
        return False


async def send_via_gmail(
    to_email: str,
    task: ExtractedTask,
    event_link: str | None,
    oauth_service=None,
) -> bool:
    """Send email using Gmail API."""
    try:
        from googleapiclient.discovery import build

        creds = oauth_service.get_credentials() if oauth_service else None
        if not creds:
            logger.error({"action": "email_error", "provider": "gmail", "error": "no credentials"})
            return False

        service = build("gmail", "v1", credentials=creds)
        settings = get_settings()

        message = MIMEText(_build_email_body(task, event_link))
        message["to"] = to_email
        message["from"] = settings.sender_email
        message["subject"] = f"TaskPilot AI: {task.title} scheduled"

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        logger.info({"action": "email_sent", "provider": "gmail", "to": to_email})
        return True
    except Exception as e:
        logger.error({"action": "email_error", "provider": "gmail", "error": str(e)})
        return False


async def send_notification(
    to_email: str,
    task: ExtractedTask,
    event_link: str | None = None,
    oauth_service=None,
) -> bool:
    """Route to the configured email provider."""
    settings = get_settings()
    if settings.email_provider == "gmail":
        return await send_via_gmail(to_email, task, event_link, oauth_service)
    return await send_via_resend(to_email, task, event_link)
