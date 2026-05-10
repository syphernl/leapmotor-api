# Vehicle Model Differences

Documentation of the differences in API response format and signal IDs
across the various Leapmotor vehicle models.

---

## Table of Contents

- [Overview](#overview)
- [Status Response Format](#status-response-format)
  - [T03 — Named Fields](#t03--named-fields)
  - [C10/B10 — Numeric Signal IDs](#c10b10--numeric-signal-ids)
- [Status Endpoint Path](#status-endpoint-path)
- [Signal ID to Named Field Mapping](#signal-id-to-named-field-mapping)
  - [Battery and Charging](#battery-and-charging)
  - [Driving and Movement](#driving-and-movement)
  - [GPS Location](#gps-location)
  - [Climate Control](#climate-control)
  - [Doors and Locks](#doors-and-locks)
  - [Windows](#windows)
  - [Tire Pressure](#tire-pressure)
  - [Seat and Comfort](#seat-and-comfort)
  - [Security and Exterior](#security-and-exterior)
  - [Ignition](#ignition)
  - [Timestamp](#timestamp)
  - [Charge Plan (config.3)](#charge-plan-config3)
- [Unmapped Signal IDs](#unmapped-signal-ids)
- [B10-Specific Differences vs C10](#b10-specific-differences-vs-c10)
- [Full C10 Response Example](#full-c10-response-example)

---

## Overview

| Feature | T03 | C10 | B10 |
|---|---|---|---|
| Status format | Named fields | Signal IDs | Signal IDs |
| Endpoint path | `/status/get/t03` | `/status/get/c10` | `/status/get/c10` ¹ |
| Config/charge plan | Flat fields or `config.3` | `config.3` | `config.3` |
| API `carType` value | `T03` | `C10` | `B10` |
| Privacy flags | ✓ | ✓ | ✓ |

¹ The B10 reports `carType=B10` in the vehicle list, but the backend uses
the C10 endpoint. The library performs the mapping automatically.

---

## Status Response Format

### T03 — Named Fields

The T03 returns data as human-readable JSON fields directly at the
`data` level:

```json
{
  "code": 0,
  "data": {
    "soc": 85,
    "chargeState": 0,
    "chargeRemainTime": 0,
    "batteryCurrent": 0.0,
    "batteryVoltage": 400.0,
    "dcInputFastCharge": 0,
    "dumpEnergy": 45000,
    "expectedMileage": 300,
    "speed": 0,
    "totalMileage": 15000,
    "gearStatus": 0,
    "latitude": 45.123,
    "longitude": 7.456,
    "acSwitch": false,
    "acSetting": 22.0,
    "driverDoorLockStatus": true,
    "lbcmDriverDoorStatus": false,
    "bbcmBackDoorStatus": false,
    "leftFrontTirePressure": 250,
    "rightFrontTirePressure": 255,
    "leftRearTirePressure": 260,
    "rightRearTirePressure": 245,
    "collectTime": "2026-05-07 10:30:00",
    "chargesocSetting": 80,
    "chargeTimeSetting": "22:00"
  }
}
```

### C10/B10 — Numeric Signal IDs

The C10 and B10 models return data in a `signal` dictionary with numeric
keys (signal IDs from the APK), plus a separate `config` object:

```json
{
  "code": 0,
  "data": {
    "privacyGPS": 1,
    "privacyData": 1,
    "signal": {
      "1204": 65,
      "1178": 0.1,
      "1177": 424.9,
      "1149": 0,
      "1197": 0,
      "1200": 0,
      "3260": 278,
      "1319": 0.0,
      "1318": 3030,
      "1010": 0,
      "3725": 40.858,
      "3724": 14.283,
      "1938": 0,
      "2183": 23.0,
      "1298": 1,
      "1277": 0,
      "1281": 0,
      "2667": 253,
      "2653": 250,
      "2646": 255,
      "2660": 253,
      "sts": 1778137347360
    },
    "config": {
      "3": {
        "percent": 100,
        "isEnable": 0,
        "beginTime": "22:00",
        "endTime": "08:00",
        "cycles": "1,1,1,1,1,1,1",
        "circulation": 1,
        "recharge": 0,
        "updateTime": "2026-05-06 08:54:48"
      }
    }
  }
}
```

The library automatically converts signal IDs to named fields via
`_merge_signal_to_named()` in `models.py`, ensuring that `VehicleStatus.from_dict()`
works uniformly across all models.

---

## Status Endpoint Path

| API `carType` | Endpoint path |
|---|---|
| `T03` | `/carownerservice/oversea/vehicle/v1/status/get/t03` |
| `C10` | `/carownerservice/oversea/vehicle/v1/status/get/c10` |
| `B10` | `/carownerservice/oversea/vehicle/v1/status/get/c10` ¹ |

¹ The B10 does not have a dedicated endpoint; it uses the C10 one.

---

## Signal ID to Named Field Mapping

### Battery and Charging

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `1204` | `soc` | State of Charge (%) | `int` |
| `100003` | `preciseSoc` | Precise SOC (%) | `float` |
| `1200` | `chargeRemainTime` | Remaining charge time (minutes) | `int` |
| `1178` | `batteryCurrent` | Battery current (A) | `float` |
| `1177` | `batteryVoltage` | Battery voltage (V) | `float` |
| `1197` | `dcInputFastCharge` | DC fast charge status | `int` |
| `1149` | `chargeState` | Connection: 0=Disconnected, 1=AC, 2=DC | `int` |
| `1182` | `minBatteryTemp` | Minimum battery temperature (°C) | `int` |
| `1186` | `batteryThermalRequest` | Battery thermal request: 4=Heating | `int` |
| `3736` | `chargeCompleted` | Charge completed: 0=No, 1=Yes | `int` |

### Driving and Movement

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `1319` | `speed` | Speed (km/h) | `float` |
| `1318` | `totalMileage` | Total odometer (km) | `int` |
| `1010` | `gearStatus` | Gear: 0=Park, 1=Drive, 2=Neutral, 3=Reverse (`GearStatus` enum) | `int` |
| `1944` | `vehicleState` | Vehicle state: 0,1,3=Parked, 2,4,5=Driving | `int` |
| `1941` | `drivingState` | Driving state: 1,2,4=Parked, 3,5=Driving | `int` |
| `6048` | `speedLimit` | Speed limit (km/h) | `int` |
| `6047` | `speedLimitUnit` | Speed limit unit | `int` |
| `12054` | `speedLimitActive` | Speed limit active: 0=No, 1=Yes | `int` |
| `3260` | `expectedMileage` | Estimated remaining range (km) | `int` |
| `2188` | `liveRemainingRange` | Live remaining range (km) | `int` |
| `3257` | `maxRange` | CLTC/WLTP max range (km) | `int` |
| `3262` | `rangeMode` | Range mode: 0=CLTC, 1=WLTP | `int` |

### GPS Location

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `3725` | `latitude` | Latitude | `float` |
| `3724` | `longitude` | Longitude | `float` |

> Signals `2190`/`2191` are used as **automatic GPS fallback** by the library
> when the primary coordinates (`3725`/`3724`) are absent.

### Climate Control

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `1938` | `acSwitch` | A/C status (0=off, 1=on) | `int` |
| `2183` | `acSetting` | Left set temperature (°C) | `float` |
| `2184` | `acSettingRight` | Right set temperature (°C) | `float` |
| `1349` | `interiorTemp` | Interior temperature (°C) | `float` |
| `1943` | `recirculationMode` | Air recirculation mode | `int` |
| `1945` | `windshieldDefrost` | Windshield defrost active | `int` |
| `1946` | `rearWindowHeating` | Rear window heating active | `int` |
| `3713` | `climateMode` | Climate mode: 0=Off, 1=Fast cool, 3=Fast heat | `int` |
| `2669` | `rapidCooling` | Rapid cooling active | `int` |
| `2681` | `rapidHeating` | Rapid heating active | `int` |

### Doors and Locks

| Signal ID | Named Field | Description | Type/Values |
|---|---|---|---|
| `1298` | `driverDoorLockStatus` | Lock status: 1=Locked, 0=Unlocked | `int` |
| `1277` | `lbcmDriverDoorStatus` | Driver door: 0=Closed, 1=Open | `int` |
| `1278` | `rbcmDriverDoorStatus` | Passenger door: 0=Closed, 1=Open | `int` |
| `1279` | `lbcmLeftRearDoorStatus` | Left rear door: 0=Closed, 1=Open | `int` |
| `1280` | `rbcmRightRearDoorStatus` | Right rear door: 0=Closed, 1=Open | `int` |
| `1281` | `bbcmBackDoorStatus` | Tailgate: 0=Closed, 1=Open | `int` |

### Windows

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `3727` | `leftFrontWindowPercent` | Left front window opening (%) | `int` |
| `3728` | `rightFrontWindowPercent` | Right front window opening (%) | `int` |
| `1879` | `leftRearWindowPercent` | Left rear window opening (%) | `int` |
| `1880` | `rightRearWindowPercent` | Right rear window opening (%) | `int` |
| `1693` | `driverWindowStatus` | Driver window: 0=Closed, 1=Open | `int` |
| `1694` | `rightFrontWindowStatus` | Right front window: 0=Closed, 1=Open | `int` |
| `1695` | `leftRearWindowStatus` | Left rear window: 0=Closed, 1=Open | `int` |
| `1696` | `rightRearWindowStatus` | Right rear window: 0=Closed, 1=Open | `int` |

### Tire Pressure

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `2667` | `leftFrontTirePressure` | Left front pressure (kPa × 100) | `int` |
| `2653` | `rightFrontTirePressure` | Right front pressure (kPa × 100) | `int` |
| `2646` | `leftRearTirePressure` | Left rear pressure (kPa × 100) | `int` |
| `2660` | `rightRearTirePressure` | Right rear pressure (kPa × 100) | `int` |
| `2641` | `leftFrontTirePressureState` | Left front alarm: 0=OK | `int` |
| `2648` | `rightFrontTirePressureState` | Right front alarm: 0=OK | `int` |
| `2655` | `leftRearTirePressureState` | Left rear alarm: 0=OK | `int` |
| `2662` | `rightRearTirePressureState` | Right rear alarm: 0=OK | `int` |

> ⚠️ **B10 note:** The tire pressure sensor mapping may be inverted
> compared to the C10 (see [B10-Specific Differences](#b10-specific-differences-vs-c10)).

### Seat and Comfort

These signals are mapped to `SeatComfortStatus` (C10/B10 only; T03 does not
report these).

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `2100` | `driverSeatHeating` | Driver seat heating level | `int` |
| `2101` | `driverSeatVentilation` | Driver seat ventilation level | `int` |
| `2118` | `passengerSeatHeating` | Passenger seat heating level | `int` |
| `2119` | `passengerSeatVentilation` | Passenger seat ventilation level | `int` |
| `1816` | `steeringWheelHeating` | Steering wheel heating | `int` |
| `1624` | `steeringWheelHeaterMinutes` | Steering wheel heater remaining minutes | `int` |

### Security and Exterior

These signals are mapped to `SecurityStatus` (C10/B10 only).

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `1255` | `vehicleSecurityActive` | Vehicle security active | `int` |
| `3636` | `sentryMode` | Sentry mode | `int` |
| `49` | `leftMirrorHeating` | Left mirror heating | `int` |
| `50` | `rightMirrorHeating` | Right mirror heating | `int` |
| `1724` | `roofOpening` | Roof/skylight opening status | `int` |

### Ignition

| Signal ID | Named Field | Description | Type |
|---|---|---|---|
| `1256` | `bcmKeyPositionOn1` | Key position ON1: 0=Off, 1=On | `int` |
| `1257` | `bcmKeyPositionOn2` | Key position ON2: 0=Off, 1=On | `int` |
| `1258` | `bcmKeyPositionOn3` | Key position ON3: 0=Off, 1=On | `int` |

### Timestamp

| Signal ID | Named Field | Description |
|---|---|---|
| `sts` | `collectTime` ¹ | Data collection timestamp (epoch ms) |

¹ The `sts` value is an epoch in milliseconds; the library converts it to
a `collectTime` string in `YYYY-MM-DD HH:MM:SS` format for consistency
with the T03 format.

### Charge Plan (config.3)

The C10/B10 charge plan is stored in `config.3` (not in `signal`). The library
automatically maps these to `ChargePlan` fields (via `battery.charge_plan`):

| config.3 key | ChargePlan field | Description |
|---|---|---|
| `percent` | `soc_setting` | Charge SOC limit (%) |
| `isEnable` | `enabled` | Schedule enabled: 0=No, 1=Yes |
| `beginTime` | `start` | Schedule start time (e.g. `"22:00"`) |
| `endTime` | `end` | Schedule end time (e.g. `"08:00"`) |
| `cycles` | `cycles` | Active days (e.g. `"1,1,1,1,1,1,1"`) |
| `circulation` | `circulation` | Recurrence flag |
| `recharge` | `recharge` | Recharge flag |

---

## Unmapped Signal IDs

These signals are present in C10/B10 responses but are **not** currently
mapped to `VehicleStatus` fields. They are available in the raw response
(`VehicleStatus.raw`) and via `normalize_vehicle()` diagnostics.

| Signal ID | Description | Type |
|---|---|---|
| `47` | Legacy plug-in status: 0=No, 1=Yes | `int` |
| `1480` | Parking camera status | `int` |
| `1939` | AC status / fan mode | `int` |
| `1949` | (Undocumented) | `int` |
| `2190` | GPS latitude (used as auto-fallback) | `float` |
| `2191` | GPS longitude (used as auto-fallback) | `float` |
| `3273` | (Undocumented — seen value 100) | `int` |
| `3366` | (Undocumented) | `int` |
| `3709` | (Undocumented) | `int` |
| `3710` | (Undocumented — seen value 1) | `int` |
| `3711` | (Undocumented) | `int` |
| `3712` | (Undocumented — seen value 1) | `int` |
| `3734` | (Undocumented) | `int` |
| `3735` | (Undocumented) | `int` |
| `3737` | (Undocumented — seen value 1) | `int` |
| `100010`–`100017` | Battery module voltages (V) | `str`/`int` |

---

## B10-Specific Differences vs C10

### Status Endpoint

The B10 does **not** have a dedicated `/status/get/b10` endpoint. The API
returns HTTP 404 if `b10` is used in the path. The library automatically
maps `b10` → `c10` in the endpoint path.

### Tire Pressure

The `kerniger/leapmotor-ha` repo reports that the B10 tire pressure sensors
have an **inverted** mapping compared to the C10:

| Position | C10 (signal ID) | B10 (signal ID) |
|---|---|---|
| Front left | `2667` | `2646` |
| Front right | `2653` | `2653` |
| Rear left | `2646` | `2660` |
| Rear right | `2660` | `2667` |

This means that for the B10, signal `2667` corresponds to the rear right
tire (not front left as in the C10). This difference is handled in the
`normalize_vehicle()` function of the `kerniger/leapmotor-ha` repo but is
**not** yet reflected in the `_SIGNAL_TO_NAMED` mapping in `models.py`,
which uses the C10 mapping for both.

### `seatLayout` and `rudder` Fields

The B10 returns `seatLayout` and `rudder` as **integers** in the vehicle
list, while other models may return them as strings. The library converts
both to `str` in `Vehicle.from_dict()` for consistency.

---

## Full C10 Response Example

This is a real (anonymized) response from the status endpoint for a C10:

```json
{
  "code": 0,
  "result": 0,
  "message": "Request successful",
  "data": {
    "privacyGPS": 1,
    "signal": {
      "47": 0,
      "49": 0,
      "50": 0,
      "1010": 0,
      "1149": 0,
      "1177": 424.9,
      "1178": 0.1,
      "1182": 18,
      "1186": 0,
      "1197": 0,
      "1204": 65,
      "1255": 2,
      "1256": 0,
      "1257": 0,
      "1258": 0,
      "1277": 0,
      "1278": 0,
      "1279": 0,
      "1280": 0,
      "1281": 0,
      "1298": 1,
      "1318": 3030,
      "1319": 0.0,
      "1349": 21.5,
      "1480": 1,
      "1624": 2,
      "1693": 0,
      "1694": 0,
      "1695": 0,
      "1696": 0,
      "1724": 100,
      "1816": 0,
      "1879": 0,
      "1880": 0,
      "1938": 0,
      "1939": 1,
      "1941": 1,
      "1943": 0,
      "1944": 0,
      "1945": 0,
      "1946": 0,
      "1949": 0,
      "2100": 0,
      "2101": 0,
      "2118": 0,
      "2119": 0,
      "2183": 23.0,
      "2188": 278,
      "2190": 40.858536,
      "2191": 14.283342,
      "2641": 0,
      "2646": 255,
      "2648": 0,
      "2653": 250,
      "2655": 0,
      "2660": 253,
      "2662": 0,
      "2667": 253,
      "2669": 0,
      "2681": 0,
      "3257": 283,
      "3260": 278,
      "3262": 1,
      "3273": 100,
      "3366": 0,
      "3636": 0,
      "3709": 0,
      "3710": 1,
      "3711": 0,
      "3712": 1,
      "3713": 0,
      "3724": 14.28319,
      "3725": 40.85812,
      "3727": 0,
      "3728": 0,
      "3734": 0,
      "3735": 0,
      "3736": 0,
      "3737": 1,
      "6047": 0,
      "6048": 110,
      "12054": 0,
      "100003": 65.3,
      "100010": "0.0",
      "100011": "175.8",
      "100012": "175.8",
      "100013": "0.0",
      "100014": "172.7",
      "100015": "172.7",
      "100016": "172.7",
      "100017": 68,
      "sts": 1778137347360,
      "1": 1778137344969,
      "2": 14.28319,
      "3": 40.85812
    },
    "config": {
      "3": {
        "cycles": "1,1,1,1,1,1,1",
        "endTime": "08:00",
        "percent": 100,
        "isEnable": 0,
        "recharge": 0,
        "beginTime": "22:00",
        "updateTime": "2026-05-06 08:54:48",
        "circulation": 1
      },
      "4": {
        "mac": "58D15A6FE2C7",
        "version": "2.0",
        "updateTime": "2026-03-13 14:03:04"
      }
    },
    "privacyData": 1
  }
}
```

### Reading the Example

| Signal | Value | Meaning |
|---|---|---|
| `1204` = 65 | SOC 65% | |
| `100003` = 65.3 | Precise SOC 65.3% | |
| `3260` = 278 | Remaining range 278 km | |
| `3257` = 283 | WLTP range 283 km | |
| `3262` = 1 | WLTP mode | |
| `1319` = 0.0 | Speed 0 km/h (stationary) | |
| `1318` = 3030 | Odometer 3030 km | |
| `1010` = 0 | Gear P (park) | |
| `1298` = 1 | Doors locked | |
| `1277`–`1281` = 0 | All doors closed | |
| `1149` = 0 | Not connected to charger | |
| `1178` = 0.1 | Current 0.1 A (idle) | |
| `1177` = 424.9 | Voltage 424.9 V | |
| `1349` = 21.5 | Interior temperature 21.5°C | |
| `2183` = 23.0 | Climate set to 23.0°C | |
| `1938` = 0 | A/C off | |
| `3725`/`3724` | GPS 40.858°N 14.283°E | |
| `config.3.percent` = 100 | Charge limit 100% | |
| `config.3.isEnable` = 0 | Scheduling disabled | |
