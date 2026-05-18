from app.agents.base import BaseAgent
from app.config import POSSIBLE_ACTIONS


class PlanningAgent(BaseAgent):
    """Decides what actions should be executed based on the user's intent and extracted details."""

    name = "planning_agent"

    def get_system_prompt(self) -> str:
        return f"""You are a Planning Agent for TaskPilot AI.

Your job is to determine which actions should be executed based on the user's intent and extracted details.

Available actions:
{POSSIBLE_ACTIONS}

Rules for deciding actions:
- If intent is "meeting": always include "create_calendar_event"
- If intent is "task": always include "create_task"
- If intent is "reminder": always include "set_reminder"
- If intent is "reschedule": always include "reschedule_event"
- If notification is "email": add "send_email"
- If notification is "whatsapp": add "send_whatsapp"
- If the user mentions "send email" or "email to team": add "send_email"
- If the user mentions "send whatsapp" or "whatsapp": add "send_whatsapp"

Return ONLY valid JSON in this exact format:
{{"actions": ["list of action strings"]}}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return f"""User command: {context.get("text", "")}
Intent: {context.get("intent", "")}
Title: {context.get("title", "")}
Notification: {context.get("notification", "none")}
Task category: {context.get("task_category", "other")}"""
