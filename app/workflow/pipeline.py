from app.agents.intent_agent import IntentAgent
from app.agents.extraction_agent import ExtractionAgent
from app.agents.calendar_agent import CalendarContextAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.reminder_agent import ReminderAgent
from app.agents.prioritization_agent import PrioritizationAgent
from app.agents.summary_agent import SummaryAgent
from app.models import AgentResponse
from app.utils.date_parser import resolve_relative_date, resolve_relative_time


class Pipeline:
    """Orchestrates all 9 agents in sequence, passing accumulated context."""

    def __init__(self):
        self.intent_agent = IntentAgent()
        self.extraction_agent = ExtractionAgent()
        self.calendar_agent = CalendarContextAgent()
        self.scheduler_agent = SchedulerAgent()
        self.planning_agent = PlanningAgent()
        self.notification_agent = NotificationAgent()
        self.reminder_agent = ReminderAgent()
        self.prioritization_agent = PrioritizationAgent()
        self.summary_agent = SummaryAgent()

    def run(self, user_text: str) -> AgentResponse:
        """Run the full agent pipeline and return a structured AgentResponse."""
        context = {"text": user_text}

        # Step 1: Intent Detection
        intent_result = self.intent_agent.process(context)
        context["intent"] = intent_result.get("intent", "")

        # Step 2: Information Extraction
        extraction_result = self.extraction_agent.process(context)
        context.update({
            "title": extraction_result.get("title", ""),
            "date": extraction_result.get("date", ""),
            "time": extraction_result.get("time", ""),
            "attendees": extraction_result.get("attendees", []),
            "notification": extraction_result.get("notification", "none"),
            "task_category": extraction_result.get("task_category", "other"),
        })

        # Step 3: Calendar Context
        calendar_result = self.calendar_agent.process(context)
        context["busy_slots"] = calendar_result.get("busy_slots", [])
        context["conflict_detected"] = calendar_result.get("conflict_detected", False)

        # Step 4: Smart Scheduling
        scheduler_result = self.scheduler_agent.process(context)
        context["alternative_slot"] = scheduler_result.get("alternative_slot", "")

        # Step 5: Action Planning
        planning_result = self.planning_agent.process(context)
        context["actions"] = planning_result.get("actions", [])

        # Step 6: Notification Generation
        notification_result = self.notification_agent.process(context)
        context["message"] = notification_result.get("message", "")

        # Step 7: Reminder Intelligence
        reminder_result = self.reminder_agent.process(context)
        context["reminder_time"] = reminder_result.get("reminder_time", "")

        # Step 8: Prioritization
        prioritization_result = self.prioritization_agent.process(context)
        context["priority_order"] = prioritization_result.get("priority_order", [])

        # Step 9: Summary / Agenda
        summary_result = self.summary_agent.process(context)
        context["agenda"] = summary_result.get("agenda", [])

        # Resolve relative dates and times for the final response
        resolved_date = resolve_relative_date(context.get("date", ""))
        resolved_time = resolve_relative_time(context.get("time", ""))

        # Build the final response
        response = AgentResponse(
            intent=context.get("intent", ""),
            title=context.get("title", ""),
            date=resolved_date or context.get("date", ""),
            time=resolved_time or context.get("time", ""),
            attendees=context.get("attendees", []),
            notification=context.get("notification", "none"),
            actions=context.get("actions", []),
            message=context.get("message", ""),
            alternative_slot=context.get("alternative_slot", ""),
            busy_slots=context.get("busy_slots", []),
            reminder_time=context.get("reminder_time", ""),
            priority_order=context.get("priority_order", []),
            agenda=context.get("agenda", []),
        )

        return response
