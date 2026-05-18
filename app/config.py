import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.1"))
MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "1024"))

POSSIBLE_INTENTS = ["meeting", "task", "reminder", "reschedule"]

POSSIBLE_ACTIONS = [
    "create_calendar_event",
    "create_task",
    "set_reminder",
    "send_email",
    "send_whatsapp",
    "reschedule_event",
]