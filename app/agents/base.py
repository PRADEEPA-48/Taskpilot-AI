import json
import re
from abc import ABC, abstractmethod
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, MODEL_NAME, MODEL_TEMPERATURE, MODEL_MAX_TOKENS


class BaseAgent(ABC):
    """Base class for all TaskPilot AI agents."""

    name: str = "base_agent"

    def __init__(self):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=MODEL_NAME,
            temperature=MODEL_TEMPERATURE,
            max_tokens=MODEL_MAX_TOKENS,
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    def build_human_message(self, context: dict) -> str:
        """Build the human message from the accumulated context."""
        return json.dumps(context, indent=2)

    def parse_json_response(self, raw: str) -> dict:
        """Extract and parse JSON from the LLM response."""
        # Try to find JSON block in the response
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        # Fallback: try parsing the whole string
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def process(self, context: dict) -> dict:
        """Run the agent and return parsed JSON output."""
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=self.build_human_message(context)),
        ]
        response = self.llm.invoke(messages)
        return self.parse_json_response(response.content)
