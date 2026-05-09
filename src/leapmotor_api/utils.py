"""Utility functions for leapmotor api."""

from datetime import UTC, datetime, timedelta, timezone


def previous_week_window_seconds(tz: timezone = UTC) -> tuple[int, int]:
    """Return the previous Monday–Sunday window used by getLastweekEC."""
    now = datetime.now(tz=tz)
    this_monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    start = this_monday - timedelta(days=7)
    end = this_monday - timedelta(seconds=1)
    return int(start.timestamp()), int(end.timestamp())
