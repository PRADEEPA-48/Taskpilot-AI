from app.agents.base import BaseAgent


class ReminderAgent(BaseAgent):
    """Generates smart reminder timings based on the event type."""

    name = "reminder_agent"

    def get_system_prompt(self) -> str:
        return """You are a Reminder Intelligence Agent for TaskPilot AI.

Your job is to determine the optimal reminder timing based on the event type and category.

Rules for reminder timing:
- Meeting: "30 mins before"
- Study/Study session: "1 hour before"
- Task: "15 mins before"
- Reminder: "At the time of event"
- Work/Professional meeting: "15 mins before"
- Health/Exercise: "30 mins before"
- Personal: "15 mins before"
- If rescheduling: keep the same reminder timing as before

Return ONLY valid JSON in this exact format:
{
  "reminder_time": "the recommended reminder timing"
}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return f"""Intent: {context.get("intent", "")}
Title: {context.get("title", "")}
Task category: {context.get("task_category", "other")}
Date: {context.get("date", "")}
Time: {context.get("time", "")}"""
