"""Remote-control action mappings.

This module is separated from :mod:`const` to avoid circular imports
between ``const`` and ``models``.
"""

from __future__ import annotations

from .const import (
    REMOTE_CTL_AC_SWITCH,
    REMOTE_CTL_BATTERY_PREHEAT,
    REMOTE_CTL_BATTERY_PREHEAT_OFF,
    REMOTE_CTL_BATTERY_PREHEAT_ON,
    REMOTE_CTL_CHARGE_LIMIT,
    REMOTE_CTL_CHARGE_START,
    REMOTE_CTL_CHARGE_STOP,
    REMOTE_CTL_FIND_CAR,
    REMOTE_CTL_LOCK,
    REMOTE_CTL_QUICK_COOL,
    REMOTE_CTL_QUICK_HEAT,
    REMOTE_CTL_SEND_DESTINATION,
    REMOTE_CTL_SENTRY_MODE,
    REMOTE_CTL_SENTRY_MODE_OFF,
    REMOTE_CTL_SENTRY_MODE_ON,
    REMOTE_CTL_STEERING_WHEEL_HEAT,
    REMOTE_CTL_STEERING_WHEEL_HEAT_OFF,
    REMOTE_CTL_STEERING_WHEEL_HEAT_ON,
    REMOTE_CTL_SUNSHADE,
    REMOTE_CTL_SUNSHADE_CLOSE,
    REMOTE_CTL_SUNSHADE_OPEN,
    REMOTE_CTL_TRUNK,
    REMOTE_CTL_TRUNK_CLOSE,
    REMOTE_CTL_TRUNK_OPEN,
    REMOTE_CTL_UNLOCK,
    REMOTE_CTL_UNLOCK_CHARGER,
    REMOTE_CTL_WINDOWS,
    REMOTE_CTL_WINDOWS_CLOSE,
    REMOTE_CTL_WINDOWS_OPEN,
    REMOTE_CTL_WINDSHIELD_DEFROST,
)
from .models import (
    BatteryPreheatValue,
    CarType,
    ChargeToggleValue,
    ClimateCircle,
    ClimateMode,
    ClimateOperate,
    ClimatePosition,
    ClimateWindshield,
    LockValue,
    RemoteActionCtlBatteryPreheat,
    RemoteActionCtlChargePlan,
    RemoteActionCtlClimate,
    RemoteActionCtlFindCar,
    RemoteActionCtlLock,
    RemoteActionCtlSendDestination,
    RemoteActionCtlSentryMode,
    RemoteActionCtlSteeringWheelHeat,
    RemoteActionCtlSunshade,
    RemoteActionCtlToggleCharge,
    RemoteActionCtlTrunk,
    RemoteActionCtlUnlockCharger,
    RemoteActionCtlWindows,
    RemoteActionSpec,
    SentryModeValue,
    SteeringWheelHeatValue,
    SunshadeValue,
    ToggleValue,
    VehicleAbility,
    VehicleRight,
    WindowsValue,
)

REMOTE_ACTION_SPECS: dict[str, RemoteActionSpec] = {
    REMOTE_CTL_UNLOCK: RemoteActionCtlLock(value=LockValue.UNLOCK, required_right=VehicleRight.LOCK),
    REMOTE_CTL_LOCK: RemoteActionCtlLock(value=LockValue.LOCK, required_right=VehicleRight.LOCK),
    REMOTE_CTL_UNLOCK_CHARGER: RemoteActionCtlUnlockCharger(required_right=VehicleRight.UNLOCK_CHARGER),
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
    REMOTE_CTL_BATTERY_PREHEAT_ON: RemoteActionCtlBatteryPreheat(
        value=BatteryPreheatValue.ON, required_right=VehicleRight.BATTERY_PREHEAT
    ),
    REMOTE_CTL_BATTERY_PREHEAT_OFF: RemoteActionCtlBatteryPreheat(
        value=BatteryPreheatValue.OFF, required_right=VehicleRight.BATTERY_PREHEAT
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
        windlevel=4,
        wshld=ClimateWindshield.NORMAL,
        required_right=VehicleRight.CLIMATE,
    ),
    REMOTE_CTL_QUICK_COOL: RemoteActionCtlClimate(
        circle=ClimateCircle.IN,
        mode=ClimateMode.COLD,
        operate=ClimateOperate.MANUAL,
        position=ClimatePosition.ALL,
        temperature="18",
        windlevel=7,
        wshld=ClimateWindshield.NORMAL,
        required_right=VehicleRight.QUICK_CLIMATE,
    ),
    REMOTE_CTL_QUICK_HEAT: RemoteActionCtlClimate(
        circle=ClimateCircle.IN,
        mode=ClimateMode.HOT,
        operate=ClimateOperate.MANUAL,
        position=ClimatePosition.ALL,
        temperature="32",
        windlevel=7,
        wshld=ClimateWindshield.NORMAL,
        required_right=VehicleRight.QUICK_CLIMATE,
    ),
    REMOTE_CTL_WINDSHIELD_DEFROST: RemoteActionCtlClimate(
        circle=ClimateCircle.IN,
        mode=ClimateMode.HOT,
        operate=ClimateOperate.MANUAL,
        position=ClimatePosition.ALL,
        temperature="32",
        windlevel=7,
        wshld=ClimateWindshield.DEFROST,
        required_right=VehicleRight.WINDSHIELD_DEFROST,
    ),
    REMOTE_CTL_CHARGE_LIMIT: RemoteActionCtlChargePlan(required_right=VehicleRight.CHARGE_LIMIT),
    REMOTE_CTL_SEND_DESTINATION: RemoteActionCtlSendDestination(required_right=VehicleRight.SEND_DESTINATION),
    REMOTE_CTL_SENTRY_MODE: RemoteActionCtlSentryMode(
        value=SentryModeValue.ON, required_right=VehicleRight.SENTRY_MODE
    ),
    REMOTE_CTL_SENTRY_MODE_ON: RemoteActionCtlSentryMode(
        value=SentryModeValue.ON, required_right=VehicleRight.SENTRY_MODE
    ),
    REMOTE_CTL_SENTRY_MODE_OFF: RemoteActionCtlSentryMode(
        value=SentryModeValue.OFF, required_right=VehicleRight.SENTRY_MODE
    ),
    REMOTE_CTL_CHARGE_START: RemoteActionCtlToggleCharge(
        value=ChargeToggleValue.START, required_right=VehicleRight.TOGGLE_CHARGE
    ),
    REMOTE_CTL_CHARGE_STOP: RemoteActionCtlToggleCharge(
        value=ChargeToggleValue.STOP, required_right=VehicleRight.TOGGLE_CHARGE
    ),
    REMOTE_CTL_STEERING_WHEEL_HEAT: RemoteActionCtlSteeringWheelHeat(
        value=SteeringWheelHeatValue.ON, required_right=VehicleRight.STEERING_WHEEL_HEAT
    ),
    REMOTE_CTL_STEERING_WHEEL_HEAT_ON: RemoteActionCtlSteeringWheelHeat(
        value=SteeringWheelHeatValue.ON, required_right=VehicleRight.STEERING_WHEEL_HEAT
    ),
    REMOTE_CTL_STEERING_WHEEL_HEAT_OFF: RemoteActionCtlSteeringWheelHeat(
        value=SteeringWheelHeatValue.OFF, required_right=VehicleRight.STEERING_WHEEL_HEAT
    ),
}

# ---------------------------------------------------------------------------
# Car-type path mapping
# ---------------------------------------------------------------------------

# The international backend reports carType=B10 in the vehicle list,
# but the status endpoint is shared with C10.  B11 also uses the C10 path.
# Use ``CarType(car_type_str).status_path`` for runtime resolution.
CAR_TYPE_PATH_MAP: dict[str, str] = {
    CarType.B10: CarType.C10,
    CarType.B11: CarType.C10,
}

# ---------------------------------------------------------------------------
# Ability → Right relationship mapping
# ---------------------------------------------------------------------------
# Documents which VehicleAbility codes enable which VehicleRight codes.
# The server computes this; the mapping is informational for consumers.
# Based on decompiled international APK ``CarAblityToPerManager.ablityToPer()``.

ABILITY_TO_RIGHTS: dict[VehicleAbility, list[VehicleRight]] = {
    VehicleAbility.BASE: [VehicleRight.LOCK],
    VehicleAbility.STATUS_DATA: [VehicleRight.FIND_CAR],
    VehicleAbility.TRUNK: [VehicleRight.TRUNK],
    VehicleAbility.AUTOPARK: [VehicleRight.AUTOPARK],
    VehicleAbility.AC_ON: [VehicleRight.CLIMATE],
    VehicleAbility.AC_PRESET: [VehicleRight.QUICK_CLIMATE],
    VehicleAbility.LOCK_UNLOCK: [VehicleRight.BATTERY_PREHEAT],
    VehicleAbility.FIND_CAR: [VehicleRight.SUNSHADE],
    VehicleAbility.WINDOWS_C10: [VehicleRight.WINDOWS],
    VehicleAbility.WINDOWS_T03: [VehicleRight.WINDOWS],
    VehicleAbility.SEAT_HEATING: [VehicleRight.SEAT_HEAT],
    VehicleAbility.STEERING_WHEEL: [VehicleRight.STEERING_WHEEL_HEAT],
    VehicleAbility.CLIMATE_ADVANCED: [VehicleRight.QUICK_CLIMATE],
    VehicleAbility.WINDSHIELD_DEFROST: [VehicleRight.WINDSHIELD_DEFROST],
    VehicleAbility.TRUNK_SPECIAL: [VehicleRight.TRUNK],
    VehicleAbility.CYCLIC_CHARGE: [VehicleRight.SUNROOF],
    VehicleAbility.GPS_SHARING: [VehicleRight.SEND_DESTINATION],
    VehicleAbility.MILEAGE_ENERGY: [],
    VehicleAbility.SPEED_LIMIT: [VehicleRight.SPEED_LIMIT],
    VehicleAbility.CHARGE_LIMIT: [VehicleRight.CHARGE_LIMIT],
    VehicleAbility.PREPARE: [VehicleRight.PREPARE_CAR, VehicleRight.PREPARE_CAR_ALARM],
    VehicleAbility.FUEL_HEATING: [VehicleRight.FUEL_HEATING],
    VehicleAbility.SENTINEL: [VehicleRight.SENTRY_MODE],
    VehicleAbility.NAVIGATION: [VehicleRight.SEND_DESTINATION],
    VehicleAbility.DRIVER_SEAT_VENTILATION: [VehicleRight.SEAT_VENTILATION],
    VehicleAbility.PASSENGER_SEAT_VENTILATION: [VehicleRight.SEAT_VENTILATION],
    VehicleAbility.UNLOCK_CHARGE_GUN: [VehicleRight.UNLOCK_CHARGER],
}

# Rights restricted to T03/S01 only — these models have a limited
# feature set compared to C-platform and B-platform models.
T03_S01_SUPPORTED_RIGHTS: frozenset[VehicleRight] = frozenset(
    {
        VehicleRight.LOCK,
        VehicleRight.FIND_CAR,
        VehicleRight.TRUNK,
        VehicleRight.CLIMATE,
        VehicleRight.QUICK_CLIMATE,
        VehicleRight.SEND_DESTINATION,
        VehicleRight.BATTERY_PREHEAT,
        VehicleRight.SUNSHADE,
        VehicleRight.SENTRY_MODE,
        VehicleRight.WINDOWS,
        VehicleRight.SKYLIGHT,
        VehicleRight.CHARGE_LIMIT,
        VehicleRight.WINDSHIELD_DEFROST,
        VehicleRight.SUNROOF,
        VehicleRight.AUTOPARK,
    }
)
