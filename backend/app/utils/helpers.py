"""
Utility helpers: date parsing, token encryption, misc.
"""
import re
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateutil_parser


def parse_natural_date(date_str: str, time_str: str) -> tuple[datetime, datetime]:
    """
    Convert natural language date/time strings to datetime objects.
    Returns (start_dt, end_dt) where end_dt = start_dt + 1 hour.
    """
    now = datetime.now(timezone.utc)

    # Handle relative keywords
    lower = date_str.lower().strip()
    if lower == "today":
        base = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif lower == "tomorrow":
        base = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            base = dateutil_parser.parse(date_str, default=now)
        except Exception:
            base = now

    # Parse time component
    try:
        time_parsed = dateutil_parser.parse(time_str, default=base)
        start_dt = base.replace(
            hour=time_parsed.hour,
            minute=time_parsed.minute,
            second=0,
            microsecond=0,
        )
    except Exception:
        start_dt = base.replace(hour=9, minute=0, second=0, microsecond=0)

    end_dt = start_dt + timedelta(hours=1)
    return start_dt, end_dt


def sanitize_text(text: str) -> str:
    """Remove excessive whitespace from input text."""
    return re.sub(r"\s+", " ", text).strip()
