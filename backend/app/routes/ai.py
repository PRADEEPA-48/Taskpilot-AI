"""
AI processing routes: /process and /voice-command.
Runs the full pipeline: AI extraction → Calendar event → Email notification.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import TextInput, VoiceInput, ProcessResponse
from app.agents.task_agent import get_task_agent
from app.services.calendar_service import CalendarService
from app.services.email_service import send_notification
from app.services.oauth_service import get_oauth_service
from app.utils.helpers import sanitize_text
from app.utils.logger import get_logger

router = APIRouter(tags=["AI Processing"])
logger = get_logger(__name__)


async def _run_pipeline(text: str, user_email: str | None) -> ProcessResponse:
    """Shared pipeline: extract → create event → send email."""
    text = sanitize_text(text)

    # 1. AI extraction
    agent = get_task_agent()
    try:
        task = await agent.extract(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 2. Create calendar event
    oauth = get_oauth_service()
    cal = CalendarService(oauth)
    event_id = None
    event_link = None
    try:
        created = await cal.create_event(task)
        event_id = created.get("id")
        event_link = created.get("htmlLink")
    except HTTPException:
        raise
    except Exception as e:
        logger.error({"action": "pipeline_calendar_error", "error": str(e)})
        raise HTTPException(status_code=502, detail=f"Calendar error: {e}")

    # 3. Send email notification (non-fatal)
    notification_sent = False
    if user_email:
        notification_sent = await send_notification(
            to_email=user_email,
            task=task,
            event_link=event_link,
            oauth_service=oauth,
        )

    return ProcessResponse(
        success=True,
        task=task,
        event_id=event_id,
        event_link=event_link,
        notification_sent=notification_sent,
        message="Task scheduled successfully.",
    )


@router.post("/process", response_model=ProcessResponse, summary="Process natural language task")
async def process_text(body: TextInput):
    """
    Accept natural language input, extract task details via AI,
    create a Google Calendar event, and send a confirmation email.
    """
    logger.info({"action": "process_request", "text": body.text})
    return await _run_pipeline(body.text, body.user_email)


@router.post("/voice-command", response_model=ProcessResponse, summary="Process voice command")
async def voice_command(body: VoiceInput):
    """
    Accept speech-to-text converted input and run the same pipeline as /process.
    """
    logger.info({"action": "voice_command_request", "text": body.text})
    return await _run_pipeline(body.text, body.user_email)
