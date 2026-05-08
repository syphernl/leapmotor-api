"""Utility functions for parsing and deriving vehicle status from raw signal data."""

from __future__ import annotations

from typing import Any


def _safe_int(raw: Any) -> int | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None
