from app.agents.base import BaseAgent


class CalendarContextAgent(BaseAgent):
    """Analyzes existing calendar schedule and identifies busy slots."""

    name = "calendar_agent"

    def get_system_prompt(self) -> str:
        return """You are a Calendar Context Agent for TaskPilot AI.

Your job is to analyze the user's existing schedule and identify busy time slots that might conflict with the new event.

Given the user's command and extracted details, determine:
- Are there any scheduling conflicts with the requested time?
- What time slots are already occupied on that date?

Currently, you have access to a mock schedule. In production, this will be connected to Google Calendar API.

For now, simulate realistic busy slots based on common patterns:
- Typical work hours: 9 AM - 6 PM may have meetings
- Lunch hour: 12 PM - 1 PM often busy
- If the requested time seems like a common meeting time, consider it might be busy

If the requested time slot appears to be free based on the context, return an empty busy_slots list.

Return ONLY valid JSON in this exact format:
{
  "busy_slots": ["list of occupied time slots on that date, e.g., 4 PM, 5 PM"],
  "conflict_detected": true or false
}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return f"""User command: {context.get("text", "")}
Intent: {context.get("intent", "")}
Title: {context.get("title", "")}
Date: {context.get("date", "")}
Time: {context.get("time", "")}"""
