from app.agents.base import BaseAgent
from app.config import POSSIBLE_INTENTS


class IntentAgent(BaseAgent):
    """Detects the user intent from a natural language command."""

    name = "intent_agent"

    def get_system_prompt(self) -> str:
        return f"""You are an Intent Detection Agent for a productivity assistant called TaskPilot AI.

Your job is to analyze the user's natural language command and classify it into exactly one of these intents:
{POSSIBLE_INTENTS}

Rules:
- "meeting" - user wants to schedule or organize a meeting
- "task" - user wants to create a task or to-do item
- "reminder" - user wants to set a reminder for something
- "reschedule" - user wants to change an existing event's time or date

The user may speak in a mix of English and Tamil (e.g., "schedule pannu", "reminder podu", "naalaiku").
Translate and understand the intent regardless of language mix.

Return ONLY valid JSON in this exact format:
{{"intent": "one_of_the_intents"}}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return context.get("text", "")
