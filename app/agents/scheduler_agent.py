from app.agents.base import BaseAgent


class SchedulerAgent(BaseAgent):
    """Handles smart scheduling decisions, conflict detection, and alternative slot suggestions."""

    name = "scheduler_agent"

    def get_system_prompt(self) -> str:
        return """You are a Scheduler Agent for TaskPilot AI.

Your job is to make smart scheduling decisions based on the extracted details and calendar context.

Responsibilities:
- If there is a scheduling conflict, suggest the nearest available alternative time slot
- If there is no conflict, confirm the requested time and leave alternative_slot empty
- Consider reasonable time adjustments (e.g., if 5 PM is busy, suggest 6 PM or 4 PM)
- Prefer later slots over earlier ones when suggesting alternatives
- Keep the alternative in a reasonable range (within 2-3 hours of the requested time)

Return ONLY valid JSON in this exact format:
{
  "alternative_slot": "suggested time if conflict exists, empty string if no conflict",
  "conflict_detected": true or false
}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return f"""Title: {context.get("title", "")}
Date: {context.get("date", "")}
Time: {context.get("time", "")}
Busy slots: {context.get("busy_slots", [])}
Conflict detected: {context.get("conflict_detected", False)}"""
