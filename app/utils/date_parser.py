"""Date and time parsing utilities for TaskPilot AI.

Handles relative date expressions (Tomorrow, Naalaiku, etc.)
and common time formats.
"""

from datetime import datetime, timedelta
import re


# Tamil-English date mappings
TAMIL_DATE_MAP = {
    "naalaiku": "tomorrow",
    "naalai": "tomorrow",
    "iniya": "day after tomorrow",
    "matram": "day after tomorrow",
    "innaiku": "today",
    "innaikku": "today",
}

TAMIL_TIME_KEYWORDS = {
    "kalai": "morning",
    "maalai": "evening",
    "mathiyam": "noon",
    "iravu": "night",
}


def resolve_relative_date(date_str: str) -> str:
    """Resolve a relative date string to an actual date.

    Args:
        date_str: A relative date like "Tomorrow", "Naalaiku", "Today", etc.

    Returns:
        A formatted date string (YYYY-MM-DD), or the original string if unresolvable.
    """
    if not date_str:
        return ""

    normalized = date_str.strip().lower()

    # Check Tamil mappings
    for tamil_word, english_equiv in TAMIL_DATE_MAP.items():
        if tamil_word in normalized:
            normalized = english_equiv
            break

    today = datetime.now()

    if normalized == "today":
        return today.strftime("%Y-%m-%d")
    elif normalized == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif normalized in ("day after tomorrow", "day-after-tomorrow"):
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    elif "next week" in normalized:
        return (today + timedelta(weeks=1)).strftime("%Y-%m-%d")
    elif "next monday" in normalized:
        days_ahead = 0 - today.weekday() + 7
        if days_ahead <= 0:
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # Try to parse as an absolute date
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %d", "%b %d"):
        try:
            parsed = datetime.strptime(normalized, fmt)
            if parsed.year == 1900:
                parsed = parsed.replace(year=today.year)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Return original if we can't resolve
    return date_str


def resolve_relative_time(time_str: str) -> str:
    """Normalize a time string into a standard format.

    Args:
        time_str: A time like "5 PM", "7 PM", "17:00", etc.

    Returns:
        A formatted time string (HH:MM AM/PM), or the original string if unresolvable.
    """
    if not time_str:
        return ""

    normalized = time_str.strip()

    # Replace Tamil time keywords
    lower = normalized.lower()
    for tamil_word, english_equiv in TAMIL_TIME_KEYWORDS.items():
        if tamil_word in lower:
            normalized = normalized.lower().replace(tamil_word, english_equiv)
            break

    # Try to parse common time formats
    for fmt in ("%I %p", "%I:%M %p", "%I%p", "%H:%M", "%H:%M:%S"):
        try:
            parsed = datetime.strptime(normalized, fmt)
            return parsed.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            continue

    # Return original if we can't resolve
    return time_str
