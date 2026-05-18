"""
AI Agent: uses LangChain + Groq to extract structured task data
from natural language input.
"""
import json
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from app.models.schemas import ExtractedTask
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

EXTRACTION_PROMPT = """\
You are a scheduling assistant. Extract scheduling information from the user's input.

Return ONLY valid JSON matching this schema:
{{
  "title": "<event title, properly capitalized>",
  "date": "<date string, e.g. Tomorrow, 2024-12-25, Monday>",
  "time": "<time string, e.g. 5 PM, 14:00>",
  "type": "<meeting | task>",
  "notify": "<email | popup | none>"
}}

Rules:
- If no reminder is mentioned, set notify to "email" by default.
- If no type is clear, default to "meeting".
- If date is missing, use "Today".
- If time is missing, use "9 AM".
- Return ONLY the JSON object, no extra text.

User input: {text}
"""


class TaskAgent:
    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model="llama3-8b-8192",
            temperature=0,
            max_tokens=256,
        )
        self.parser = PydanticOutputParser(pydantic_object=ExtractedTask)
        self.prompt = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)

    async def extract(self, text: str) -> ExtractedTask:
        """Extract structured task data from natural language text."""
        logger.info({"action": "agent_extract", "input": text})

        chain = self.prompt | self.llm
        response = await chain.ainvoke({"text": text})
        raw = response.content.strip()

        logger.info({"action": "agent_raw_response", "raw": raw})

        # Parse JSON from LLM response
        try:
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw.strip())
            task = ExtractedTask(**data)
        except Exception as e:
            logger.error({"action": "agent_parse_error", "error": str(e), "raw": raw})
            raise ValueError(f"AI could not extract a valid task from input: {e}")

        logger.info({"action": "agent_extracted", "task": task.model_dump()})
        return task


# Singleton instance
_agent: TaskAgent | None = None


def get_task_agent() -> TaskAgent:
    global _agent
    if _agent is None:
        _agent = TaskAgent()
    return _agent
