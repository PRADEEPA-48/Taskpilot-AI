from app.agents.base import BaseAgent


class PrioritizationAgent(BaseAgent):
    """Prioritizes tasks intelligently based on urgency and importance."""

    name = "prioritization_agent"

    def get_system_prompt(self) -> str:
        return """You are a Prioritization Agent for TaskPilot AI.

Your job is to prioritize the current task/event among any existing tasks, and rank them by urgency and importance.

Prioritization rules:
- Meetings with attendees are high priority
- Time-sensitive events (happening soon) are high priority
- Study/work tasks are medium priority
- Personal tasks are lower priority
- Reminders for critical things should be prioritized
- If there is only one task, return it as the only item in the priority order
- If the intent is "reminder", include the task in the priority list

For now, if there are no other tasks to compare with, just return the current task in a single-item list, or an empty list if it's a meeting (not a task).

Return ONLY valid JSON in this exact format:
{
  "priority_order": ["list of task titles ranked by priority, highest first"]
}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return f"""Intent: {context.get("intent", "")}
Title: {context.get("title", "")}
Task category: {context.get("task_category", "other")}
Date: {context.get("date", "")}
Time: {context.get("time", "")}"""
