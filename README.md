# leapmotor-api

[![PyPI version](https://img.shields.io/pypi/v/leapmotor-api)](https://pypi.org/project/leapmotor-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/leapmotor-api)](https://pypi.org/project/leapmotor-api/)
[![License](https://img.shields.io/github/license/markoceri/leapmotor-api)](https://github.com/markoceri/leapmotor-api/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/leapmotor-api)](https://pypi.org/project/leapmotor-api/)
[![CI](https://github.com/markoceri/leapmotor-api/actions/workflows/ci.yml/badge.svg)](https://github.com/markoceri/leapmotor-api/actions)
[![codecov](https://codecov.io/gh/markoceri/leapmotor-api/graph/badge.svg)](https://codecov.io/gh/markoceri/leapmotor-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/type--checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20me-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/markoceri)

Unofficial Python client for the Leapmotor vehicle cloud API.

Extracted from the [leapmotor-ha](https://github.com/kerniger/leapmotor-ha) Home Assistant integration
to provide a reusable, framework-agnostic library.

## Acknowledgments

Special thanks to [Jakob Kern](https://github.com/kerniger) for the impressive reverse engineering work on the Leapmotor application and for generously sharing his work.

## Installation

```bash
pip install leapmotor-api
```

### Certificates

The library requires the Leapmotor app certificate and private key to authenticate API requests.
Download them from the dedicated repository:

```bash
wget https://github.com/markoceri/leapmotor-certs/archive/refs/tags/v1.0.0.zip
unzip v1.0.0.zip
```

The extracted folder contains `app_cert.pem` and `app_key.pem`. Pass their paths to the client via `app_cert_path` and `app_key_path`.

## Quick Start

```python
from leapmotor_api import LeapmotorApiClient

client = LeapmotorApiClient(
    username="user@example.com",
    password="password",
    app_cert_path="/path/to/app_cert.pem",
    app_key_path="/path/to/app_key.pem",
)

client.login()
vehicles = client.get_vehicle_list()

for vehicle in vehicles:
    status = client.get_vehicle_status(vehicle)
    print(f"{vehicle.vin} — Battery: {status.battery.soc}% — Range: {status.battery.expected_mileage} km")

client.close()
```

### Async Usage

```python
from leapmotor_api import LeapmotorApiClient
from leapmotor_api.async_client import AsyncLeapmotorApiClient

sync_client = LeapmotorApiClient(
    username="user@example.com",
    password="password",
    app_cert_path="/path/to/app_cert.pem",
    app_key_path="/path/to/app_key.pem",
)
client = AsyncLeapmotorApiClient(sync_client)

await client.login()
vehicles = await client.get_vehicle_list()
status = await client.get_vehicle_status(vehicles[0])
await client.close()
```

## Vehicle Status

`get_vehicle_status()` returns a `VehicleStatus` dataclass with typed sub-objects:

| Sub-object | Key fields |
|---|---|
| `status.battery` | `soc`, `expected_mileage`, `charge_state`, `is_charging`, `charging_power_kw`, `battery_power`, `dump_energy_kwh` |
| `status.driving` | `speed`, `total_mileage`, `gear_status`, `is_parked` |
| `status.location` | `latitude`, `longitude` |
| `status.climate` | `ac_switch`, `ac_setting`, `outdoor_temp`, `interior_temp` |
| `status.doors` | `is_locked`, `bbcm_back_door_status` |
| `status.windows` | `left_front_window_percent`, `right_front_window_percent`, `sun_shade` |
| `status.tires` | `front_left_bar`, `front_right_bar`, `rear_left_bar`, `rear_right_bar`, `all_ok` |
| `status.connectivity` | `bluetooth_state`, `hotspot_state` |
| `status.seat_comfort` | `driver_seat_heating`, `driver_seat_ventilation`, `steering_wheel_heating` |
| `status.security` | `vehicle_security_active`, `sentry_mode`, `roof_opening` |
| `status.ignition` | `bcm_key_position_on1`, `bcm_key_position_on3` |

Top-level convenience properties: `status.is_locked`, `status.is_charging`, `status.is_parked`, `status.is_regening`, `status.tire_pressure_bar`.

All fields are `T | None` — they are populated only when the vehicle reports the corresponding signal.

For raw API data, use `get_vehicle_raw_status()` or access `status.raw`.

## Remote Control

Remote actions require the vehicle PIN (`operation_password`):

```python
client = LeapmotorApiClient(..., operation_password="1234")
client.login()

client.lock_vehicle("WLM...")
client.unlock_vehicle("WLM...")
client.open_trunk("WLM...")
client.close_trunk("WLM...")
client.find_vehicle("WLM...")
client.open_windows("WLM...")
client.close_windows("WLM...")
client.ac_switch("WLM...")
client.quick_cool("WLM...")
client.quick_heat("WLM...")
client.windshield_defrost("WLM...")
client.open_sunshade("WLM...")
client.close_sunshade("WLM...")
client.battery_preheat("WLM...")
client.set_charge_limit("WLM...", charge_limit_percent=80)
```

> [!TIP]
> Consider creating a **shared/secondary account** in the Leapmotor app and sharing the vehicle with it. This avoids conflicts with your primary account sessions (e.g. being logged out from the phone app or **temporary account locks** on Leapmotor's servers).

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | `str` | — | Leapmotor account email |
| `password` | `str` | — | Leapmotor account password |
| `app_cert_path` | `str` | — | Path to app certificate PEM |
| `app_key_path` | `str` | — | Path to app private key PEM |
| `operation_password` | `str \| None` | `None` | Vehicle PIN (required for remote control) |
| `language` | `str` | `"en-GB"` | API language (`en-GB`, `it-IT`, `de-DE`, `fr-FR`, …) |
| `verify_ssl` | `bool` | `False` | Verify server TLS certificate |
| `base_url` | `str` | `DEFAULT_BASE_URL` | API base URL |
| `timeout` | `int` | `30` | HTTP timeout in seconds |
| `device_id` | `str \| None` | `None` | Custom device ID (auto-generated if omitted) |

Token refresh is handled **automatically** — all methods detect expired tokens and transparently refresh or re-login. See `token_refresh()` for manual control.

## Documentation

- [API Reference](docs/api.md) — endpoints, cryptography and remote commands
- [Vehicle Model Differences](docs/vehicles.md) — API response format and signal IDs across vehicle models

## Contributing

Interested in contributing? Read the [contributing guide](CONTRIBUTING.md) for development setup, testing, and PR guidelines.

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).