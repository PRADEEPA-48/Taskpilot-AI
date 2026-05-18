# TaskPilot AI — Backend

A production-ready FastAPI backend for a voice-enabled Agentic AI assistant that schedules tasks and meetings via Google Calendar.

---

## Tech Stack

- **FastAPI** + **Uvicorn**
- **LangChain** + **Groq** (LLM)
- **Google Calendar API** + **Google OAuth 2.0**
- **Gmail API** or **Resend** (email)
- **Python 3.11**

---

## Setup

### 1. Clone & install

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in all values in .env
```

### 3. Google Cloud Console setup

1. Create a project at https://console.cloud.google.com
2. Enable **Google Calendar API** and **Gmail API**
3. Create OAuth 2.0 credentials (Web application)
4. Add `http://localhost:8000/auth/callback` as an authorized redirect URI
5. Copy Client ID and Secret to `.env`

### 4. Run locally

```bash
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

---

## Authentication Flow

1. Visit `GET /auth/login` — redirects to Google consent screen
2. Google redirects to `GET /auth/callback?code=...`
3. Tokens are stored locally; all subsequent API calls use them automatically

---

## API Endpoints

### `POST /process`
Process natural language input through the full pipeline.

**Request:**
```json
{
  "text": "Tomorrow 5 PM hackathon meeting schedule pannu",
  "user_email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "task": {
    "title": "Hackathon Meeting",
    "date": "Tomorrow",
    "time": "5 PM",
    "type": "meeting",
    "notify": "email"
  },
  "event_id": "abc123xyz",
  "event_link": "https://calendar.google.com/event?eid=...",
  "notification_sent": true,
  "message": "Task scheduled successfully."
}
```

---

### `GET /events?days=7`
Fetch upcoming calendar events.

**Response:**
```json
{
  "events": [
    {
      "id": "abc123",
      "title": "Hackathon Meeting",
      "start": "2024-12-26T17:00:00+00:00",
      "end": "2024-12-26T18:00:00+00:00",
      "description": "Type: meeting\nCreated by TaskPilot AI",
      "html_link": "https://calendar.google.com/..."
    }
  ],
  "count": 1
}
```

---

### `POST /voice-command`
Same as `/process` — accepts speech-to-text converted input.

**Request:**
```json
{
  "text": "Schedule a team standup tomorrow at 9 AM",
  "user_email": "user@example.com"
}
```

---

### `GET /health`
Health check.

```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Deployment

### Docker

```bash
docker build -t taskpilot-ai .
docker run -p 8000:8000 --env-file .env taskpilot-ai
```

### Render

1. Push to GitHub
2. Create a new **Web Service** on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env.example`

Or use the included `render.yaml` for one-click deploy.

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for LLM |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL |
| `EMAIL_PROVIDER` | `resend` or `gmail` |
| `RESEND_API_KEY` | Resend API key (if using Resend) |
| `SENDER_EMAIL` | From address for emails |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `SECRET_KEY` | App secret key |
