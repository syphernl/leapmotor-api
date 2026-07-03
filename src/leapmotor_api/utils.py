"""Utility functions for leapmotor api."""

import json
from datetime import UTC, datetime, timedelta, timezone

_SEAT_COMFORT_POSITIONS = frozenset({"driver", "copilot"})


def build_seat_comfort_payload(position: str, level: int) -> str:
    """Build the seat heating/ventilation payload (cmd_id 301/370).

    The international app sends ``{"position": ..., "level": ...}`` rather than the
    older ``"position,level"`` string. ``position`` is ``"driver"`` or
    ``"copilot"``; ``level`` is 0 (off) to 3 (max). Payload verified against a
    live C10 (passenger ventilation level 2).
    """
    if position not in _SEAT_COMFORT_POSITIONS:
        raise ValueError(f"Unsupported seat position: {position!r}")
    if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 3:
        raise ValueError(f"Seat comfort level must be an integer from 0 to 3: {level!r}")
    return json.dumps({"position": position, "level": str(level)}, separators=(",", ":"))


def previous_week_window_seconds(tz: timezone = UTC) -> tuple[int, int]:
    """Return the previous Monday–Sunday window used by getLastweekEC."""
    now = datetime.now(tz=tz)
    this_monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    start = this_monday - timedelta(days=7)
    end = this_monday - timedelta(seconds=1)
    return int(start.timestamp()), int(end.timestamp())
