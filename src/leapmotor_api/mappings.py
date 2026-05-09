"""Remote-control action mappings.

This module is separated from :mod:`const` to avoid circular imports
between ``const`` and ``models``.
"""

from __future__ import annotations

from .const import (
    REMOTE_CTL_AC_SWITCH,
    REMOTE_CTL_BATTERY_PREHEAT,
    REMOTE_CTL_CHARGE_LIMIT,
    REMOTE_CTL_FIND_CAR,
    REMOTE_CTL_LOCK,
    REMOTE_CTL_QUICK_COOL,
    REMOTE_CTL_QUICK_HEAT,
    REMOTE_CTL_SUNSHADE,
    REMOTE_CTL_SUNSHADE_CLOSE,
    REMOTE_CTL_SUNSHADE_OPEN,
    REMOTE_CTL_TRUNK,
    REMOTE_CTL_TRUNK_CLOSE,
    REMOTE_CTL_TRUNK_OPEN,
    REMOTE_CTL_UNLOCK,
    REMOTE_CTL_WINDOWS,
    REMOTE_CTL_WINDOWS_CLOSE,
    REMOTE_CTL_WINDOWS_OPEN,
    REMOTE_CTL_WINDSHIELD_DEFROST,
)
from .models import (
    BatteryPreheatValue,
    ClimateCircle,
    ClimateMode,
    ClimateOperate,
    ClimatePosition,
    ClimateWindshield,
    LockValue,
    RemoteActionCtlBatteryPreheat,
    RemoteActionCtlChargeLimit,
    RemoteActionCtlClimate,
    RemoteActionCtlFindCar,
    RemoteActionCtlLock,
    RemoteActionCtlSunshade,
    RemoteActionCtlTrunk,
    RemoteActionCtlWindows,
    RemoteActionSpec,
    SunshadeValue,
    ToggleValue,
    VehicleRight,
    WindowsValue,
)

REMOTE_ACTION_SPECS: dict[str, RemoteActionSpec] = {
    REMOTE_CTL_UNLOCK: RemoteActionCtlLock(value=LockValue.UNLOCK, required_right=VehicleRight.LOCK),
    REMOTE_CTL_LOCK: RemoteActionCtlLock(value=LockValue.LOCK, required_right=VehicleRight.LOCK),
    REMOTE_CTL_TRUNK: RemoteActionCtlTrunk(value=ToggleValue.TRUE, required_right=VehicleRight.TRUNK),
    REMOTE_CTL_TRUNK_OPEN: RemoteActionCtlTrunk(value=ToggleValue.TRUE, required_right=VehicleRight.TRUNK),
    REMOTE_CTL_TRUNK_CLOSE: RemoteActionCtlTrunk(value=ToggleValue.FALSE, required_right=VehicleRight.TRUNK),
    REMOTE_CTL_FIND_CAR: RemoteActionCtlFindCar(value=ToggleValue.TRUE, required_right=VehicleRight.FIND_CAR),
    REMOTE_CTL_SUNSHADE: RemoteActionCtlSunshade(value=SunshadeValue.OPEN, required_right=VehicleRight.SUNSHADE),
    REMOTE_CTL_SUNSHADE_OPEN: RemoteActionCtlSunshade(value=SunshadeValue.OPEN, required_right=VehicleRight.SUNSHADE),
    REMOTE_CTL_SUNSHADE_CLOSE: RemoteActionCtlSunshade(value=SunshadeValue.CLOSE, required_right=VehicleRight.SUNSHADE),
    REMOTE_CTL_BATTERY_PREHEAT: RemoteActionCtlBatteryPreheat(
        value=BatteryPreheatValue.ON, required_right=VehicleRight.BATTERY_PREHEAT
    ),
    REMOTE_CTL_WINDOWS: RemoteActionCtlWindows(value=WindowsValue.OPEN, required_right=VehicleRight.WINDOWS),
    REMOTE_CTL_WINDOWS_OPEN: RemoteActionCtlWindows(value=WindowsValue.OPEN, required_right=VehicleRight.WINDOWS),
    REMOTE_CTL_WINDOWS_CLOSE: RemoteActionCtlWindows(value=WindowsValue.CLOSE, required_right=VehicleRight.WINDOWS),
    REMOTE_CTL_AC_SWITCH: RemoteActionCtlClimate(
        circle=ClimateCircle.OUT,
        mode=ClimateMode.NO_HOT_COLD,
        operate=ClimateOperate.MANUAL,
        position=ClimatePosition.ALL,
        temperature="24",
        windlevel="4",
        wshld=ClimateWindshield.NORMAL,
        required_right=VehicleRight.CLIMATE,
    ),
    REMOTE_CTL_QUICK_COOL: RemoteActionCtlClimate(
        circle=ClimateCircle.IN,
        mode=ClimateMode.COLD,
        operate=ClimateOperate.MANUAL,
        position=ClimatePosition.ALL,
        temperature="18",
        windlevel="7",
        wshld=ClimateWindshield.NORMAL,
        required_right=VehicleRight.QUICK_CLIMATE,
    ),
    REMOTE_CTL_QUICK_HEAT: RemoteActionCtlClimate(
        circle=ClimateCircle.IN,
        mode=ClimateMode.HOT,
        operate=ClimateOperate.MANUAL,
        position=ClimatePosition.ALL,
        temperature="32",
        windlevel="7",
        wshld=ClimateWindshield.NORMAL,
        required_right=VehicleRight.QUICK_CLIMATE,
    ),
    REMOTE_CTL_WINDSHIELD_DEFROST: RemoteActionCtlClimate(
        circle=ClimateCircle.IN,
        mode=ClimateMode.HOT,
        operate=ClimateOperate.MANUAL,
        position=ClimatePosition.ALL,
        temperature="32",
        windlevel="7",
        wshld=ClimateWindshield.DEFROST,
        required_right=VehicleRight.WINDSHIELD_DEFROST,
    ),
    REMOTE_CTL_CHARGE_LIMIT: RemoteActionCtlChargeLimit(required_right=VehicleRight.CHARGE_LIMIT),
}

# ---------------------------------------------------------------------------
# Car-type path mapping
# ---------------------------------------------------------------------------

# The international backend reports carType=B10 in the vehicle list,
# but the status endpoint is shared with C10.
CAR_TYPE_PATH_MAP: dict[str, str] = {
    "b10": "c10",
}
