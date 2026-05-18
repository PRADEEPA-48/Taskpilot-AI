import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import UserInput, AgentResponse
from app.workflow.pipeline import Pipeline

logger = logging.getLogger("taskpilot")

app = FastAPI(
    title="TaskPilot AI",
    description="Voice-enabled autonomous productivity assistant - AI Agent System",
    version="1.0.0",
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the pipeline once at startup
pipeline = Pipeline()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "TaskPilot AI"}


@app.post("/process", response_model=AgentResponse)
async def process_command(user_input: UserInput) -> AgentResponse:
    """Process a natural language command through the AI agent pipeline.

    Accepts plain text from the frontend (post speech-to-text conversion)
    and returns a structured JSON response with all agent outputs.
    """
    try:
        response = pipeline.run(user_input.text)
        return response
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return AgentResponse(
            intent="error",
            message=f"Error processing command: {str(e)}",
        )
