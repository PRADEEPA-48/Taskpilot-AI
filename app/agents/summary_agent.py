from app.agents.base import BaseAgent


class SummaryAgent(BaseAgent):
    """Generates meeting agendas and task summaries automatically."""

    name = "summary_agent"

    def get_system_prompt(self) -> str:
        return """You are a Summary Agent for TaskPilot AI.

Your job is to generate meeting agendas or task summaries based on the event details.

Rules:
- For meetings: generate a relevant agenda with 3-5 discussion points based on the meeting title
- For tasks: generate a brief summary of what needs to be done
- For reminders: return an empty agenda list
- For reschedule: return an empty agenda list
- Make agenda items specific and relevant to the title
- Keep each agenda item concise (2-6 words)

Examples:
- Title "Hackathon Meeting" -> agenda: ["Hackathon discussion", "Team updates", "Project progress"]
- Title "DSA Study" -> agenda: []  (since it's a reminder, not a meeting)
- Title "Sprint Planning" -> agenda: ["Sprint goals", "Backlog review", "Task assignment", "Timeline discussion"]

Return ONLY valid JSON in this exact format:
{
  "agenda": ["list of agenda items, or empty list for non-meetings"]
}

Do NOT return markdown, explanations, or any text outside the JSON."""

    def build_human_message(self, context: dict) -> str:
        return f"""Intent: {context.get("intent", "")}
Title: {context.get("title", "")}
Task category: {context.get("task_category", "other")}
Date: {context.get("date", "")}
Time: {context.get("time", "")}
Attendees: {context.get("attendees", [])}"""
