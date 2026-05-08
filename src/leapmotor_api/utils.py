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


def _safe_float(raw: Any) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _to_bar(raw: Any) -> float | None:
    if raw is None:
        return None
    try:
        return round(float(raw) / 100.0, 2)
    except (TypeError, ValueError):
        return None


def _derive_vehicle_state(signal: dict[str, Any]) -> str | None:
    """Return the movement state independent from charging state."""
    parked = _safe_int(signal.get("1298"))
    if parked == 1:
        return "parked"
    if parked == 0:
        return "driving"

    drive_status = _safe_int(signal.get("1941"))
    vehicle_state = _safe_int(signal.get("1944"))
    if drive_status in (1, 2, 4) or vehicle_state in (0, 1, 3):
        return "parked"
    if drive_status in (3, 5) or vehicle_state in (2, 4, 5):
        return "driving"

    return None


def _is_charging(signal: dict[str, Any]) -> bool:
    """Return whether the vehicle is currently charging."""
    # If the vehicle is driving, it's not charging (regen braking is not charging)
    if _derive_vehicle_state(signal) == "driving":
        return False

    remaining_charge_minutes = _safe_int(signal.get("1200"))
    charging_current_a = _safe_float(signal.get("1178"))
    if charging_current_a is not None and remaining_charge_minutes is not None:
        return abs(charging_current_a) >= 1.0

    charging_power_kw = _charging_power_kw(signal)
    if charging_power_kw is not None:
        return charging_power_kw >= 1.0 and remaining_charge_minutes is not None

    charge_status = _safe_int(signal.get("1939"))
    drive_status = _safe_int(signal.get("1941"))
    vehicle_state = _safe_int(signal.get("1944"))
    return charge_status in (1, 2, 3) and (
        remaining_charge_minutes is not None and (drive_status == 2 or vehicle_state == 0)
    )


def _charging_power_kw(signal: dict[str, Any]) -> float | None:
    """Return charging power derived from voltage and current signals."""
    current = _safe_float(signal.get("1178"))
    voltage = _safe_float(signal.get("1177"))
    if current is None or voltage is None:
        return None
    return round(current * voltage / 1000.0, 3)
