from app.agents.base import BaseAgent


class NotificationAgent(BaseAgent):
    """Generates email or WhatsApp notification messages."""

    name = "notification_agent"

    def get_system_prompt(self) -> str:
        return """You are a Notification Agent for TaskPilot AI.

Your job is to generate a clear, concise notification message based on the scheduling details.

Rules:
- The message should be professional and informative
- Include the event title, date, and time
- If a conflict was detected and an alternative slot was suggested, mention it
- For email notifications: write a formal message
- For WhatsApp notifications: write a casual, friendly message
- If no notification is needed (notification = "none"), still generate a confirmation message
- Keep the message to 1-2 sentences

Examples:
- "Hackathon meeting scheduled for tomorrow at 5 PM."
- "Reminder set for DSA Study tomorrow at 7 PM."
- "Meeting rescheduled to 6 PM due to a conflict at 5 PM."

Return ONLY valid JSON in this exact format:
{
  "message": "the notification message"
}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return f"""Intent: {context.get("intent", "")}
Title: {context.get("title", "")}
Date: {context.get("date", "")}
Time: {context.get("time", "")}
Notification type: {context.get("notification", "none")}
Alternative slot: {context.get("alternative_slot", "")}
Conflict detected: {context.get("conflict_detected", False)}"""
