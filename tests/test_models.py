"""Tests for leapmotor_api.models module."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from leapmotor_api.const import (
    DEFAULT_APP_VERSION,
    DEFAULT_CHANNEL,
    DEFAULT_DEVICE_TYPE,
    DEFAULT_LANGUAGE,
    DEFAULT_P12_ENC_ALG,
    DEFAULT_SOURCE,
)
from leapmotor_api.models import (
    ApiRequestHeaders,
    BatteryStatus,
    ChargeState,
    ClimateCircle,
    ClimateMode,
    ClimateOperate,
    ClimatePosition,
    ClimateWindshield,
    DoorStatus,
    DrivingStatus,
    Message,
    MessageList,
    ModuleRight,
    RemoteActionCtlBatteryPreheat,
    RemoteActionCtlClimate,
    RemoteActionCtlFindCar,
    RemoteActionCtlLock,
    RemoteActionCtlSunshade,
    RemoteActionCtlTrunk,
    RemoteActionCtlWindows,
    RemoteActionResult,
    RemoteActionSpec,
    TirePressure,
    Vehicle,
    VehicleAbility,
    VehicleRight,
    VehicleStatus,
)

# ---------------------------------------------------------------------------
# ApiRequestHeaders
# ---------------------------------------------------------------------------


class TestApiRequestHeaders:
    def _make_headers(self, **kwargs: Any) -> ApiRequestHeaders:
        defaults = {
            "nonce": "123456",
            "device_id": "dev1",
            "timestamp": "1700000000000",
            "sign": "abc123",
        }
        defaults.update(kwargs)
        return ApiRequestHeaders(**defaults)

    def test_frozen(self) -> None:
        h = self._make_headers()
        with pytest.raises(AttributeError):
            h.sign = "new"  # type: ignore[misc]

    def test_defaults_from_constants(self) -> None:
        h = self._make_headers()
        assert h.accept_language == DEFAULT_LANGUAGE
        assert h.channel == DEFAULT_CHANNEL
        assert h.device_type == DEFAULT_DEVICE_TYPE
        assert h.source == DEFAULT_SOURCE
        assert h.version == DEFAULT_APP_VERSION
        assert h.p12_enc_alg == DEFAULT_P12_ENC_ALG

    def test_to_dict_required_fields(self) -> None:
        h = self._make_headers()
        d = h.to_dict()
        assert d["acceptLanguage"] == DEFAULT_LANGUAGE
        assert d["channel"] == DEFAULT_CHANNEL
        assert d["deviceType"] == DEFAULT_DEVICE_TYPE
        assert d["source"] == DEFAULT_SOURCE
        assert d["version"] == DEFAULT_APP_VERSION
        assert d["nonce"] == "123456"
        assert d["deviceId"] == "dev1"
        assert d["timestamp"] == "1700000000000"
        assert d["sign"] == "abc123"

    def test_to_dict_includes_default_p12_enc_alg(self) -> None:
        h = self._make_headers()
        d = h.to_dict()
        assert d["X-P12_ENC_ALG"] == DEFAULT_P12_ENC_ALG

    def test_to_dict_excludes_none_p12_enc_alg(self) -> None:
        h = self._make_headers(p12_enc_alg=None)
        d = h.to_dict()
        assert "X-P12_ENC_ALG" not in d

    def test_to_dict_includes_content_type(self) -> None:
        h = self._make_headers(content_type="application/json")
        d = h.to_dict()
        assert d["Content-Type"] == "application/json"

    def test_override_defaults(self) -> None:
        h = self._make_headers(channel="custom", source="other", version="9.9.9")
        assert h.channel == "custom"
        assert h.source == "other"
        assert h.version == "9.9.9"

    def test_to_dict_is_mutable(self) -> None:
        h = self._make_headers()
        d = h.to_dict()
        d["userId"] = "42"
        assert "userId" in d


# ---------------------------------------------------------------------------
# Vehicle
# ---------------------------------------------------------------------------


class TestVehicle:
    def test_basic_creation(self) -> None:
        v = Vehicle(
            vin="WLMTEST123456",
            car_type="C10",
            email="test@test.com",
            plate_number="AB123CD",
            car_id="42",
            user_nickname="Owner",
            vehicle_nickname="MyCar",
            is_shared=False,
            year=2024,
        )
        assert v.vin == "WLMTEST123456"
        assert v.car_id == "42"
        assert v.car_type == "C10"
        assert v.email == "test@test.com"
        assert v.plate_number == "AB123CD"
        assert v.user_nickname == "Owner"
        assert v.vehicle_nickname == "MyCar"
        assert v.is_shared is False
        assert v.year == 2024

    def test_optional_fields_default_none(self) -> None:
        v = Vehicle(
            vin="VIN1",
            car_type="C11",
            email=None,
            plate_number=None,
            car_id=None,
            user_nickname=None,
            vehicle_nickname=None,
        )
        assert v.year is None
        assert v.rights == []
        assert v.abilities == []
        assert v.module_rights == []
        assert v.mobile_number is None
        assert v.out_color is None

    def test_shared_vehicle(self) -> None:
        v = Vehicle(
            vin="VIN2",
            car_type="C10",
            email=None,
            plate_number=None,
            car_id="10",
            user_nickname="Shared",
            vehicle_nickname="SharedCar",
            is_shared=True,
        )
        assert v.is_shared is True

    def test_from_dict(self) -> None:
        data: dict[str, Any] = {
            "vin": "WLMTEST123456",
            "carType": "C10",
            "email": "test@test.com",
            "plateNumber": "AB123CD",
            "carId": 42,
            "nickName": "Owner",
            "vinNickname": "MyCar",
            "mobileNumber": "+391234567890",
            "outColor": "white",
            "year": 2024,
            "abilities": ["1", "10", "36"],
            "rightList": "110,120,230",
            "moduleRights": "100,200",
        }
        v = Vehicle.from_dict(data, is_shared=False)
        assert v.vin == "WLMTEST123456"
        assert v.car_type == "C10"
        assert v.email == "test@test.com"
        assert v.plate_number == "AB123CD"
        assert v.car_id == "42"
        assert v.user_nickname == "Owner"
        assert v.vehicle_nickname == "MyCar"
        assert v.mobile_number == "+391234567890"
        assert v.out_color == "white"
        assert v.is_shared is False
        assert v.year == 2024
        assert v.abilities == [VehicleAbility.BASE, VehicleAbility.LOCK_UNLOCK, VehicleAbility.WINDOWS_T03]
        assert v.rights == [VehicleRight.LOCK, VehicleRight.FIND_CAR, VehicleRight.WINDOWS]
        assert v.module_rights == [ModuleRight.BASIC, ModuleRight.VEHICLE_CONTROL]
        assert v.raw == data

    def test_from_dict_shared(self) -> None:
        data: dict[str, Any] = {"vin": "VIN1", "carType": "C11", "carId": 1}
        v = Vehicle.from_dict(data, is_shared=True)
        assert v.is_shared is True
        assert v.email is None
        assert v.plate_number is None
        assert v.rights == []
        assert v.abilities == []
        assert v.module_rights == []

    def test_from_dict_real_t03_permissions(self) -> None:
        """Parse real T03 permission data."""
        data: dict[str, Any] = {
            "vin": "VIN_T03",
            "carType": "T03",
            "carId": 99,
            "rightList": "190,180,170,171,160,161,130,460,120,340,230,220,110",
            "moduleRights": "100,200,300,400",
            "abilities": [
                "1",
                "2",
                "3",
                "5",
                "7",
                "10",
                "11",
                "14",
                "15",
                "17",
                "18",
                "20",
                "30",
                "31",
                "34",
                "35",
                "36",
                "52",
                "61",
            ],
        }
        v = Vehicle.from_dict(data, is_shared=False)
        assert VehicleRight.LOCK in v.rights
        assert VehicleRight.CLIMATE in v.rights
        assert VehicleRight.WINDOWS in v.rights
        assert len(v.rights) == 13
        assert ModuleRight.BASIC in v.module_rights
        assert len(v.module_rights) == 4
        assert VehicleAbility.BASE in v.abilities
        assert VehicleAbility.NAVIGATION in v.abilities
        # Ability 61 is unknown but should parse without error
        unknown_61 = [a for a in v.abilities if a.value == 61]
        assert len(unknown_61) == 1
        assert unknown_61[0].name == "UNKNOWN_61"

    def test_unknown_right_code(self) -> None:
        """Unknown right codes create pseudo-members."""
        data: dict[str, Any] = {"vin": "V", "carType": "X", "carId": 1, "rightList": "110,999"}
        v = Vehicle.from_dict(data, is_shared=False)
        assert len(v.rights) == 2
        assert v.rights[0] == VehicleRight.LOCK
        assert v.rights[1].value == 999
        assert v.rights[1].name == "UNKNOWN_999"

    def test_has_ability(self) -> None:
        v = Vehicle(
            vin="V",
            car_type="T",
            email=None,
            plate_number=None,
            car_id=None,
            user_nickname=None,
            vehicle_nickname=None,
            abilities=[VehicleAbility.BASE, VehicleAbility.GPS],
        )
        assert v.has_ability(VehicleAbility.BASE) is True
        assert v.has_ability(1) is True
        assert v.has_ability(VehicleAbility.NAVIGATION) is False
        assert v.has_ability(52) is False

    def test_has_right(self) -> None:
        v = Vehicle(
            vin="V",
            car_type="T",
            email=None,
            plate_number=None,
            car_id=None,
            user_nickname=None,
            vehicle_nickname=None,
            rights=[VehicleRight.LOCK, VehicleRight.WINDOWS],
        )
        assert v.has_right(VehicleRight.LOCK) is True
        assert v.has_right(110) is True
        assert v.has_right(VehicleRight.TRUNK) is False

    def test_has_module_right(self) -> None:
        v = Vehicle(
            vin="V",
            car_type="T",
            email=None,
            plate_number=None,
            car_id=None,
            user_nickname=None,
            vehicle_nickname=None,
            module_rights=[ModuleRight.BASIC],
        )
        assert v.has_module_right(ModuleRight.BASIC) is True
        assert v.has_module_right(100) is True
        assert v.has_module_right(ModuleRight.VEHICLE_CONTROL) is False

    def test_enum_descriptions(self) -> None:
        assert VehicleRight.LOCK.description == "Lock / Unlock doors"
        assert VehicleAbility.BASE.description == "Vehicle base / remote state"
        assert ModuleRight.BASIC.description == "Basic authorisation (lock/unlock)"
        # Unknown codes get a fallback description
        unknown = VehicleRight(999)
        assert "Unknown" in unknown.description

    def test_non_numeric_abilities_skipped(self) -> None:
        """Non-numeric ability strings are silently skipped."""
        data: dict[str, Any] = {"vin": "V", "carType": "X", "carId": 1, "abilities": ["1", "bad", "10"]}
        v = Vehicle.from_dict(data, is_shared=False)
        assert len(v.abilities) == 2
        assert v.abilities[0] == VehicleAbility.BASE
        assert v.abilities[1] == VehicleAbility.LOCK_UNLOCK


# ---------------------------------------------------------------------------
# TirePressure
# ---------------------------------------------------------------------------


class TestTirePressure:
    def test_bar_conversion(self) -> None:
        tp = TirePressure(
            front_left_kpa=250,
            front_right_kpa=255,
            rear_left_kpa=260,
            rear_right_kpa=245,
        )
        assert tp.front_left_bar == 2.5
        assert tp.front_right_bar == 2.55
        assert tp.rear_left_bar == 2.6
        assert tp.rear_right_bar == 2.45

    def test_bar_conversion_none(self) -> None:
        tp = TirePressure()
        assert tp.front_left_bar is None
        assert tp.front_right_bar is None
        assert tp.rear_left_bar is None
        assert tp.rear_right_bar is None

    def test_all_bar_dict(self) -> None:
        tp = TirePressure(front_left_kpa=250, rear_right_kpa=260)
        result = tp.all_bar
        assert result["front_left"] == 2.5
        assert result["front_right"] is None
        assert result["rear_left"] is None
        assert result["rear_right"] == 2.6

    def test_all_ok_true(self) -> None:
        tp = TirePressure(
            front_left_state=0,
            front_right_state=0,
            rear_left_state=0,
            rear_right_state=0,
        )
        assert tp.all_ok is True

    def test_all_ok_false(self) -> None:
        tp = TirePressure(
            front_left_state=0,
            front_right_state=1,
            rear_left_state=0,
            rear_right_state=0,
        )
        assert tp.all_ok is False

    def test_all_ok_unknown(self) -> None:
        tp = TirePressure(front_left_state=0, front_right_state=0)
        assert tp.all_ok is None

    def test_frozen(self) -> None:
        tp = TirePressure(front_left_kpa=250)
        with pytest.raises(AttributeError):
            tp.front_left_kpa = 300  # type: ignore[misc]


# ---------------------------------------------------------------------------
# BatteryStatus
# ---------------------------------------------------------------------------


class TestChargeState:
    def test_enum_values(self) -> None:
        assert ChargeState.NOT_CONNECTED == 0
        assert ChargeState.AC_CONNECTED == 1
        assert ChargeState.DC_CONNECTED == 2

    def test_enum_from_int(self) -> None:
        assert ChargeState(0) is ChargeState.NOT_CONNECTED
        assert ChargeState(1) is ChargeState.AC_CONNECTED
        assert ChargeState(2) is ChargeState.DC_CONNECTED

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            ChargeState(99)


class TestBatteryStatus:
    def test_dump_energy_kwh(self) -> None:
        bs = BatteryStatus(dump_energy=45000)
        assert bs.dump_energy_kwh == 45.0

    def test_dump_energy_kwh_none(self) -> None:
        bs = BatteryStatus()
        assert bs.dump_energy_kwh is None

    def test_battery_power_positive(self) -> None:
        bs = BatteryStatus(battery_voltage=400.0, battery_current=50.0)
        assert bs.battery_power == 20.0

    def test_battery_power_negative(self) -> None:
        bs = BatteryStatus(battery_voltage=400.0, battery_current=-10.0)
        assert bs.battery_power == -4.0

    def test_battery_power_none_voltage(self) -> None:
        bs = BatteryStatus(battery_current=50.0)
        assert bs.battery_power is None

    def test_battery_power_none_current(self) -> None:
        bs = BatteryStatus(battery_voltage=400.0)
        assert bs.battery_power is None

    def test_charging_power_kw_negative_current(self) -> None:
        """Negative current means charging (current flows into battery)."""
        bs = BatteryStatus(battery_voltage=400.0, battery_current=-10.0)
        assert bs.charging_power_kw == 4.0

    def test_charging_power_kw_positive_current(self) -> None:
        """Positive current means discharging, so charging power is 0."""
        bs = BatteryStatus(battery_voltage=400.0, battery_current=10.0)
        assert bs.charging_power_kw == 0.0

    def test_charging_power_kw_none(self) -> None:
        bs = BatteryStatus()
        assert bs.charging_power_kw is None

    def test_discharging_power_kw_positive_current(self) -> None:
        """Positive current means discharging."""
        bs = BatteryStatus(battery_voltage=400.0, battery_current=50.0)
        assert bs.discharging_power_kw == 20.0

    def test_discharging_power_kw_negative_current(self) -> None:
        """Negative current means charging, so discharging power is 0."""
        bs = BatteryStatus(battery_voltage=400.0, battery_current=-10.0)
        assert bs.discharging_power_kw == 0.0

    def test_discharging_power_kw_none(self) -> None:
        bs = BatteryStatus()
        assert bs.discharging_power_kw is None

    def test_is_charging_true(self) -> None:
        """is_charging is True when charging_power_kw is available and charge_remain_time is set."""
        bs = BatteryStatus(battery_voltage=400.0, battery_current=-10.0, charge_remain_time=60)
        assert bs.is_charging is True

    def test_is_charging_false_remain_time_zero(self) -> None:
        """charge_remain_time=0 means not actually charging (vehicle off)."""
        bs = BatteryStatus(battery_voltage=400.0, battery_current=-10.0, charge_remain_time=0)
        assert bs.is_charging is False

    def test_is_charging_false_no_remain_time(self) -> None:
        bs = BatteryStatus(battery_voltage=400.0, battery_current=-10.0)
        assert bs.is_charging is False

    def test_is_charging_false_no_power_data(self) -> None:
        bs = BatteryStatus(charge_remain_time=60)
        assert bs.is_charging is False

    def test_is_charging_false_empty(self) -> None:
        bs = BatteryStatus()
        assert bs.is_charging is False

    def test_is_discharging_true(self) -> None:
        bs = BatteryStatus(battery_voltage=400.0, battery_current=50.0)
        assert bs.is_discharging is True

    def test_is_discharging_false_charging(self) -> None:
        bs = BatteryStatus(battery_voltage=400.0, battery_current=-10.0)
        assert bs.is_discharging is False

    def test_is_discharging_false_no_data(self) -> None:
        bs = BatteryStatus()
        assert bs.is_discharging is False

    def test_from_dict_full(self) -> None:
        data: dict[str, Any] = {
            "soc": 85,
            "chargeState": 1,
            "chargeRemainTime": 120,
            "chargesocSetting": 80,
            "chargeTimeSetting": "08:00",
            "dcInputFastCharge": 1,
            "dumpEnergy": 50000,
            "batteryCurrent": -15.5,
            "batteryVoltage": 400.0,
            "expectedMileage": 300,
        }
        bs = BatteryStatus.from_dict(data)
        assert bs.soc == 85
        assert bs.charge_state is ChargeState.AC_CONNECTED
        assert bs.charge_remain_time == 120
        assert bs.charge_soc_setting == 80
        assert bs.charge_time_setting == "08:00"
        assert bs.dc_input_fast_charge == 1
        assert bs.dump_energy == 50000
        assert bs.battery_current == -15.5
        assert bs.battery_voltage == 400.0
        assert bs.expected_mileage == 300

    def test_from_dict_invalid_charge_state(self) -> None:
        data: dict[str, Any] = {"chargeState": 99}
        bs = BatteryStatus.from_dict(data)
        assert bs.charge_state is None

    def test_from_dict_empty(self) -> None:
        bs = BatteryStatus.from_dict({})
        assert bs.soc is None
        assert bs.charge_state is None


# ---------------------------------------------------------------------------
# DrivingStatus
# ---------------------------------------------------------------------------


class TestDrivingStatus:
    def test_is_parked_true(self) -> None:
        ds = DrivingStatus(speed=0)
        assert ds.is_parked is True

    def test_is_parked_false(self) -> None:
        ds = DrivingStatus(speed=60)
        assert ds.is_parked is False

    def test_is_parked_none(self) -> None:
        ds = DrivingStatus()
        assert ds.is_parked is None


# ---------------------------------------------------------------------------
# DoorStatus
# ---------------------------------------------------------------------------


class TestDoorStatus:
    def test_is_locked_true(self) -> None:
        ds = DoorStatus(driver_door_lock_status=True)
        assert ds.is_locked is True

    def test_is_locked_false(self) -> None:
        ds = DoorStatus(driver_door_lock_status=False)
        assert ds.is_locked is False

    def test_is_locked_none(self) -> None:
        ds = DoorStatus()
        assert ds.is_locked is None


# ---------------------------------------------------------------------------
# VehicleStatus.from_dict
# ---------------------------------------------------------------------------


class TestVehicleStatusFromDict:
    def test_empty_dict(self) -> None:
        vs = VehicleStatus.from_dict({})
        assert vs.battery.soc is None
        assert vs.driving.speed is None
        assert vs.location.latitude is None
        assert vs.climate.ac_switch is None
        assert vs.doors.driver_door_lock_status is None
        assert vs.collect_time is None

    def test_battery_fields(self) -> None:
        data: dict[str, Any] = {
            "soc": 85,
            "chargeState": 1,
            "chargeRemainTime": 120,
            "chargesocSetting": 80,
            "dumpEnergy": 50000,
            "batteryCurrent": -15.5,
            "batteryVoltage": 400.0,
            "expectedMileage": 300,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.battery.soc == 85
        assert vs.battery.charge_state is ChargeState.AC_CONNECTED
        assert vs.battery.charge_remain_time == 120
        assert vs.battery.charge_soc_setting == 80
        assert vs.battery.dump_energy == 50000
        assert vs.battery.battery_current == -15.5
        assert vs.battery.battery_voltage == 400.0
        assert vs.battery.expected_mileage == 300

    def test_driving_fields(self) -> None:
        data: dict[str, Any] = {"speed": 80, "totalMileage": 15000, "gearStatus": 3}
        vs = VehicleStatus.from_dict(data)
        assert vs.driving.speed == 80
        assert vs.driving.total_mileage == 15000
        assert vs.driving.gear_status == 3

    def test_location_fields(self) -> None:
        data: dict[str, Any] = {"latitude": 45.123, "longitude": 7.456}
        vs = VehicleStatus.from_dict(data)
        assert vs.location.latitude == 45.123
        assert vs.location.longitude == 7.456

    def test_climate_fields(self) -> None:
        data: dict[str, Any] = {
            "acSwitch": True,
            "acSetting": 22.0,
            "outdoorTemp": 28,
            "acAirVolume": 3,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.climate.ac_switch is True
        assert vs.climate.ac_setting == 22.0
        assert vs.climate.outdoor_temp == 28
        assert vs.climate.ac_air_volume == 3

    def test_door_fields(self) -> None:
        data: dict[str, Any] = {
            "driverDoorLockStatus": True,
            "lbcmDriverDoorStatus": False,
            "bbcmBackDoorStatus": True,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.doors.driver_door_lock_status is True
        assert vs.doors.lbcm_driver_door_status is False
        assert vs.doors.bbcm_back_door_status is True

    def test_window_fields(self) -> None:
        data: dict[str, Any] = {
            "leftFrontWindowPercent": 50,
            "rightFrontWindowPercent": 0,
            "sunShade": 10,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.windows.left_front_window_percent == 50
        assert vs.windows.right_front_window_percent == 0
        assert vs.windows.sun_shade == 10

    def test_tire_fields(self) -> None:
        data: dict[str, Any] = {
            "leftFrontTirePressure": 250,
            "rightFrontTirePressure": 255,
            "leftRearTirePressure": 260,
            "rightRearTirePressure": 245,
            "leftFrontTirePressureState": 0,
            "rightFrontTirePressureState": 0,
            "leftRearTirePressureState": 0,
            "rightRearTirePressureState": 0,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.tires.front_left_kpa == 250
        assert vs.tires.front_right_kpa == 255
        assert vs.tires.all_ok is True
        assert vs.tire_pressure_bar["front_left"] == 2.5

    def test_connectivity_fields(self) -> None:
        data: dict[str, Any] = {
            "bluetoothState": True,
            "bluetoothAddr": "AA:BB:CC:DD:EE:FF",
            "hotspotState": False,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.connectivity.bluetooth_state is True
        assert vs.connectivity.bluetooth_addr == "AA:BB:CC:DD:EE:FF"
        assert vs.connectivity.hotspot_state is False

    def test_ignition_fields(self) -> None:
        data: dict[str, Any] = {"bcmKeyPositionOn1": True, "bcmKeyPositionOn3": False}
        vs = VehicleStatus.from_dict(data)
        assert vs.ignition.bcm_key_position_on1 is True
        assert vs.ignition.bcm_key_position_on3 is False

    def test_timestamps(self) -> None:
        data: dict[str, Any] = {
            "collectTime": "2024-12-25 10:30:00",
            "createTime": "2024-12-25 10:30:05",
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.collect_time == datetime(2024, 12, 25, 10, 30, 0)
        assert vs.create_time == datetime(2024, 12, 25, 10, 30, 5)

    def test_invalid_timestamp_ignored(self) -> None:
        data: dict[str, Any] = {"collectTime": "not-a-date"}
        vs = VehicleStatus.from_dict(data)
        assert vs.collect_time is None

    def test_raw_preserved(self) -> None:
        data: dict[str, Any] = {"soc": 50, "custom_field": "value"}
        vs = VehicleStatus.from_dict(data)
        assert vs.raw == data

    def test_convenience_is_locked(self) -> None:
        data: dict[str, Any] = {"driverDoorLockStatus": True}
        vs = VehicleStatus.from_dict(data)
        assert vs.is_locked is True

    def test_convenience_is_charging(self) -> None:
        data: dict[str, Any] = {
            "chargeState": 1,
            "batteryCurrent": -10.0,
            "batteryVoltage": 400.0,
            "chargeRemainTime": 60,
            "speed": 0,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_charging is True

    def test_convenience_is_charging_false_not_connected(self) -> None:
        data: dict[str, Any] = {
            "chargeState": 0,
            "batteryCurrent": -10.0,
            "batteryVoltage": 400.0,
            "chargeRemainTime": 60,
            "speed": 0,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_charging is False

    def test_convenience_is_charging_false_while_driving(self) -> None:
        data: dict[str, Any] = {
            "chargeState": 1,
            "batteryCurrent": -10.0,
            "batteryVoltage": 400.0,
            "chargeRemainTime": 60,
            "speed": 50,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_charging is False

    def test_convenience_is_regening(self) -> None:
        """Regen: battery charging while driving and not plugged in."""
        data: dict[str, Any] = {
            "chargeState": 0,
            "batteryCurrent": -5.0,
            "batteryVoltage": 400.0,
            "chargeRemainTime": 60,
            "speed": 50,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_regening is True

    def test_convenience_is_regening_false_when_parked(self) -> None:
        data: dict[str, Any] = {
            "chargeState": 0,
            "batteryCurrent": -5.0,
            "batteryVoltage": 400.0,
            "chargeRemainTime": 60,
            "speed": 0,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_regening is False

    def test_convenience_is_regening_false_when_connected(self) -> None:
        data: dict[str, Any] = {
            "chargeState": 1,
            "batteryCurrent": -5.0,
            "batteryVoltage": 400.0,
            "chargeRemainTime": 60,
            "speed": 50,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_regening is False

    def test_convenience_is_parked(self) -> None:
        data: dict[str, Any] = {"speed": 0}
        vs = VehicleStatus.from_dict(data)
        assert vs.is_parked is True

    def test_tire_pressure_property(self) -> None:
        data: dict[str, Any] = {"leftFrontTirePressure": 250}
        vs = VehicleStatus.from_dict(data)
        assert vs.tire_pressure.front_left_kpa == 250

    # -- Signal-based responses (C10/B10) --

    def test_signal_based_battery(self) -> None:
        """C10/B10 return signal IDs; they should be mapped to named fields."""
        data: dict[str, Any] = {
            "signal": {
                "1204": 65,
                "1178": 0.1,
                "1177": 424.9,
                "1197": 0,
                "1149": 0,
                "1200": 45,
                "3260": 278,
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.battery.soc == 65
        assert vs.battery.battery_current == 0.1
        assert vs.battery.battery_voltage == 424.9
        assert vs.battery.dc_input_fast_charge == 0
        assert vs.battery.charge_state is ChargeState.NOT_CONNECTED
        assert vs.battery.charge_remain_time == 45
        assert vs.battery.expected_mileage == 278

    def test_signal_based_driving(self) -> None:
        data: dict[str, Any] = {
            "signal": {"1319": 0.0, "1318": 3030, "1010": 0},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.driving.speed == 0.0
        assert vs.driving.total_mileage == 3030
        assert vs.driving.gear_status == 0

    def test_signal_based_location(self) -> None:
        data: dict[str, Any] = {
            "signal": {"3725": 40.85812, "3724": 14.28319},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.location.latitude == 40.85812
        assert vs.location.longitude == 14.28319

    def test_signal_based_doors(self) -> None:
        data: dict[str, Any] = {
            "signal": {"1298": 1, "1277": 0, "1278": 0, "1279": 0, "1280": 0, "1281": 0},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.doors.driver_door_lock_status == 1
        assert vs.is_locked is True
        assert vs.doors.lbcm_driver_door_status == 0
        assert vs.doors.bbcm_back_door_status == 0

    def test_signal_based_tires(self) -> None:
        data: dict[str, Any] = {
            "signal": {
                "2667": 253,
                "2653": 250,
                "2646": 255,
                "2660": 253,
                "2641": 0,
                "2648": 0,
                "2655": 0,
                "2662": 0,
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.tires.front_left_kpa == 253
        assert vs.tires.front_right_kpa == 250
        assert vs.tires.rear_left_kpa == 255
        assert vs.tires.rear_right_kpa == 253
        assert vs.tires.all_ok is True

    def test_signal_based_windows(self) -> None:
        data: dict[str, Any] = {
            "signal": {"3727": 0, "3728": 0, "1879": 0, "1880": 0, "1693": 0, "1694": 0},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.windows.left_front_window_percent == 0
        assert vs.windows.driver_window_status == 0

    def test_signal_based_climate(self) -> None:
        data: dict[str, Any] = {
            "signal": {"1938": 0, "2183": 23.0},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.climate.ac_switch == 0
        assert vs.climate.ac_setting == 23.0

    def test_signal_based_ignition(self) -> None:
        data: dict[str, Any] = {
            "signal": {"1256": 0, "1258": 0},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.ignition.bcm_key_position_on1 == 0
        assert vs.ignition.bcm_key_position_on3 == 0

    def test_signal_based_timestamp(self) -> None:
        data: dict[str, Any] = {
            "signal": {"sts": 1778137347360},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.collect_time is not None
        assert vs.collect_time.year == 2026

    def test_signal_based_raw_preserves_original(self) -> None:
        """raw should contain the original status_data, not the merged version."""
        data: dict[str, Any] = {"signal": {"1204": 65}}
        vs = VehicleStatus.from_dict(data)
        assert "signal" in vs.raw
        assert "soc" not in vs.raw

    def test_signal_based_named_field_priority(self) -> None:
        """Named fields already present should take priority over signals."""
        data: dict[str, Any] = {
            "soc": 90,
            "signal": {"1204": 65},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.battery.soc == 90

    def test_signal_based_full_c10_response(self) -> None:
        """Comprehensive test with a realistic C10 signal-based response."""
        data: dict[str, Any] = {
            "privacyGPS": 1,
            "signal": {
                "47": 0,
                "1204": 65,
                "1178": 0.1,
                "1177": 424.9,
                "1197": 0,
                "1149": 0,
                "3260": 278,
                "1319": 0.0,
                "1318": 3030,
                "1010": 0,
                "3725": 40.85812,
                "3724": 14.28319,
                "1938": 0,
                "2183": 23.0,
                "1298": 1,
                "1277": 0,
                "1281": 0,
                "2667": 253,
                "2653": 250,
                "2646": 255,
                "2660": 253,
                "1256": 0,
                "1258": 0,
                "sts": 1778137347360,
            },
            "config": {
                "3": {
                    "percent": 100,
                    "isEnable": 0,
                    "beginTime": "22:00",
                    "endTime": "08:00",
                },
            },
            "privacyData": 1,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.battery.soc == 65
        assert vs.battery.charge_state is ChargeState.NOT_CONNECTED
        assert vs.driving.speed == 0.0
        assert vs.driving.total_mileage == 3030
        assert vs.location.latitude == 40.85812
        assert vs.is_locked is True
        assert vs.tires.front_left_kpa == 253
        assert vs.collect_time is not None

    # -- New battery fields via from_dict --

    def test_battery_new_fields_from_dict(self) -> None:
        data: dict[str, Any] = {
            "preciseSoc": 64.8,
            "minBatteryTemp": 22,
            "batteryThermalRequest": 0,
            "chargeCompleted": 1,
            "chargeScheduleEnabled": 1,
            "chargeScheduleStart": "22:00",
            "chargeScheduleEnd": "06:00",
            "chargeScheduleCycles": "1,2,3,4,5,6,7",
            "chargeScheduleCirculation": 1,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.battery.precise_soc == 64.8
        assert vs.battery.min_battery_temp == 22
        assert vs.battery.battery_thermal_request == 0
        assert vs.battery.charge_completed == 1
        assert vs.battery.charge_schedule_enabled == 1
        assert vs.battery.charge_schedule_start == "22:00"
        assert vs.battery.charge_schedule_end == "06:00"
        assert vs.battery.charge_schedule_cycles == "1,2,3,4,5,6,7"
        assert vs.battery.charge_schedule_circulation == 1

    # -- New battery signals --

    def test_signal_battery_new_fields(self) -> None:
        data: dict[str, Any] = {
            "signal": {
                "100003": 64.8,
                "1182": 22,
                "1186": 0,
                "3736": 1,
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.battery.precise_soc == 64.8
        assert vs.battery.min_battery_temp == 22
        assert vs.battery.battery_thermal_request == 0
        assert vs.battery.charge_completed == 1

    # -- config.3 charge plan mapping --

    def test_config3_charge_plan_fields(self) -> None:
        data: dict[str, Any] = {
            "signal": {"1204": 80},
            "config": {
                "3": {
                    "percent": 90,
                    "isEnable": 1,
                    "beginTime": "23:00",
                    "endTime": "07:00",
                    "cycles": "1,2,3,4,5",
                    "circulation": 0,
                },
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.battery.charge_soc_setting == 90
        assert vs.battery.charge_schedule_enabled == 1
        assert vs.battery.charge_schedule_start == "23:00"
        assert vs.battery.charge_schedule_end == "07:00"
        assert vs.battery.charge_schedule_cycles == "1,2,3,4,5"
        assert vs.battery.charge_schedule_circulation == 0

    # -- New driving fields --

    def test_driving_new_fields(self) -> None:
        data: dict[str, Any] = {
            "vehicleState": 2,
            "drivingState": 3,
            "speedLimit": 130,
            "speedLimitUnit": 0,
            "speedLimitActive": 1,
            "liveRemainingRange": 250,
            "maxRange": 400,
            "rangeMode": 1,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.driving.vehicle_state == 2
        assert vs.driving.driving_state == 3
        assert vs.driving.speed_limit == 130
        assert vs.driving.speed_limit_unit == 0
        assert vs.driving.speed_limit_active == 1
        assert vs.driving.live_remaining_range == 250
        assert vs.driving.max_range == 400
        assert vs.driving.range_mode == 1

    def test_signal_driving_new_fields(self) -> None:
        data: dict[str, Any] = {
            "signal": {
                "1944": 2,
                "1941": 3,
                "6048": 120,
                "6047": 1,
                "12054": 0,
                "2188": 200,
                "3257": 350,
                "3262": 0,
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.driving.vehicle_state == 2
        assert vs.driving.driving_state == 3
        assert vs.driving.speed_limit == 120
        assert vs.driving.speed_limit_unit == 1
        assert vs.driving.speed_limit_active == 0
        assert vs.driving.live_remaining_range == 200
        assert vs.driving.max_range == 350
        assert vs.driving.range_mode == 0

    # -- New climate fields --

    def test_climate_new_fields(self) -> None:
        data: dict[str, Any] = {
            "acSettingRight": 21.5,
            "interiorTemp": 25.0,
            "recirculationMode": 1,
            "windshieldDefrost": 0,
            "rearWindowHeating": 1,
            "climateMode": 2,
            "rapidCooling": 0,
            "rapidHeating": 1,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.climate.ac_setting_right == 21.5
        assert vs.climate.interior_temp == 25.0
        assert vs.climate.recirculation_mode == 1
        assert vs.climate.windshield_defrost == 0
        assert vs.climate.rear_window_heating == 1
        assert vs.climate.climate_mode == 2
        assert vs.climate.rapid_cooling == 0
        assert vs.climate.rapid_heating == 1

    def test_signal_climate_new_fields(self) -> None:
        data: dict[str, Any] = {
            "signal": {
                "2184": 22.0,
                "1349": 26.5,
                "1943": 0,
                "1945": 1,
                "1946": 0,
                "3713": 1,
                "2669": 1,
                "2681": 0,
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.climate.ac_setting_right == 22.0
        assert vs.climate.interior_temp == 26.5
        assert vs.climate.recirculation_mode == 0
        assert vs.climate.windshield_defrost == 1
        assert vs.climate.rear_window_heating == 0
        assert vs.climate.climate_mode == 1
        assert vs.climate.rapid_cooling == 1
        assert vs.climate.rapid_heating == 0

    # -- Ignition bcm_key_position_on2 --

    def test_ignition_on2_field(self) -> None:
        data: dict[str, Any] = {"bcmKeyPositionOn2": True}
        vs = VehicleStatus.from_dict(data)
        assert vs.ignition.bcm_key_position_on2 is True

    def test_signal_ignition_on2(self) -> None:
        data: dict[str, Any] = {"signal": {"1257": 1}}
        vs = VehicleStatus.from_dict(data)
        assert vs.ignition.bcm_key_position_on2 == 1

    # -- SeatComfortStatus --

    def test_seat_comfort_fields(self) -> None:
        data: dict[str, Any] = {
            "driverSeatHeating": 3,
            "driverSeatVentilation": 2,
            "passengerSeatHeating": 1,
            "passengerSeatVentilation": 0,
            "steeringWheelHeating": 1,
            "steeringWheelHeaterMinutes": 15,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.seat_comfort.driver_seat_heating == 3
        assert vs.seat_comfort.driver_seat_ventilation == 2
        assert vs.seat_comfort.passenger_seat_heating == 1
        assert vs.seat_comfort.passenger_seat_ventilation == 0
        assert vs.seat_comfort.steering_wheel_heating == 1
        assert vs.seat_comfort.steering_wheel_heater_minutes == 15

    def test_signal_seat_comfort(self) -> None:
        data: dict[str, Any] = {
            "signal": {
                "2100": 2,
                "2101": 1,
                "2118": 3,
                "2119": 0,
                "1816": 1,
                "1624": 10,
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.seat_comfort.driver_seat_heating == 2
        assert vs.seat_comfort.driver_seat_ventilation == 1
        assert vs.seat_comfort.passenger_seat_heating == 3
        assert vs.seat_comfort.passenger_seat_ventilation == 0
        assert vs.seat_comfort.steering_wheel_heating == 1
        assert vs.seat_comfort.steering_wheel_heater_minutes == 10

    def test_seat_comfort_defaults(self) -> None:
        vs = VehicleStatus.from_dict({})
        assert vs.seat_comfort.driver_seat_heating is None
        assert vs.seat_comfort.steering_wheel_heater_minutes is None

    # -- SecurityStatus --

    def test_security_fields(self) -> None:
        data: dict[str, Any] = {
            "vehicleSecurityActive": 1,
            "sentryMode": 0,
            "leftMirrorHeating": 1,
            "rightMirrorHeating": 1,
            "roofOpening": 50,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.security.vehicle_security_active == 1
        assert vs.security.sentry_mode == 0
        assert vs.security.left_mirror_heating == 1
        assert vs.security.right_mirror_heating == 1
        assert vs.security.roof_opening == 50

    def test_signal_security(self) -> None:
        data: dict[str, Any] = {
            "signal": {
                "1255": 1,
                "3636": 1,
                "49": 0,
                "50": 0,
                "1724": 0,
            },
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.security.vehicle_security_active == 1
        assert vs.security.sentry_mode == 1
        assert vs.security.left_mirror_heating == 0
        assert vs.security.right_mirror_heating == 0
        assert vs.security.roof_opening == 0

    def test_security_defaults(self) -> None:
        vs = VehicleStatus.from_dict({})
        assert vs.security.vehicle_security_active is None
        assert vs.security.sentry_mode is None

    # -- GPS fallback signals --

    def test_gps_fallback_signals(self) -> None:
        """Should use alternative coordinates (2190/2191) when primary are absent."""
        data: dict[str, Any] = {
            "signal": {"2190": 45.123, "2191": 7.456},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.location.latitude == 45.123
        assert vs.location.longitude == 7.456

    def test_gps_primary_over_fallback(self) -> None:
        """Primary GPS (3725/3724) takes precedence over fallback (2190/2191)."""
        data: dict[str, Any] = {
            "signal": {"3725": 46.0, "3724": 8.0, "2190": 45.0, "2191": 7.0},
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.location.latitude == 46.0
        assert vs.location.longitude == 8.0

    # -- VehicleStatus.is_plugged --

    def test_is_plugged_true(self) -> None:
        """Plugged in but not actively charging."""
        data: dict[str, Any] = {
            "chargeState": 1,
            "speed": 0,
            "chargeRemainTime": 0,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_plugged is True
        assert vs.is_charging is False

    def test_is_plugged_false_not_connected(self) -> None:
        data: dict[str, Any] = {"chargeState": 0, "speed": 0}
        vs = VehicleStatus.from_dict(data)
        assert vs.is_plugged is False

    def test_is_plugged_false_while_charging(self) -> None:
        data: dict[str, Any] = {
            "chargeState": 1,
            "speed": 0,
            "batteryCurrent": -10.0,
            "batteryVoltage": 400.0,
            "chargeRemainTime": 60,
        }
        vs = VehicleStatus.from_dict(data)
        assert vs.is_plugged is False
        assert vs.is_charging is True


# ---------------------------------------------------------------------------
# DrivingStatus.is_parked fallbacks
# ---------------------------------------------------------------------------


class TestDrivingStatusIsParkedFallbacks:
    def test_vehicle_state_parked(self) -> None:
        assert DrivingStatus(vehicle_state=0).is_parked is True
        assert DrivingStatus(vehicle_state=1).is_parked is True
        assert DrivingStatus(vehicle_state=3).is_parked is True

    def test_vehicle_state_driving(self) -> None:
        assert DrivingStatus(vehicle_state=2).is_parked is False
        assert DrivingStatus(vehicle_state=4).is_parked is False
        assert DrivingStatus(vehicle_state=5).is_parked is False

    def test_driving_state_parked(self) -> None:
        assert DrivingStatus(driving_state=1).is_parked is True
        assert DrivingStatus(driving_state=2).is_parked is True
        assert DrivingStatus(driving_state=4).is_parked is True

    def test_driving_state_driving(self) -> None:
        assert DrivingStatus(driving_state=3).is_parked is False
        assert DrivingStatus(driving_state=5).is_parked is False

    def test_speed_takes_priority(self) -> None:
        """Speed always takes priority over vehicle_state/driving_state."""
        assert DrivingStatus(speed=0, vehicle_state=2).is_parked is True
        assert DrivingStatus(speed=50, vehicle_state=0).is_parked is False


# ---------------------------------------------------------------------------
# Vehicle.from_dict — additional fields
# ---------------------------------------------------------------------------


class TestVehicleFromDictAdditional:
    def test_seat_layout_and_rudder(self) -> None:
        data: dict[str, Any] = {
            "vin": "V",
            "carType": "C10",
            "carId": 1,
            "seatLayout": 5,
            "rudder": 1,
        }
        v = Vehicle.from_dict(data, is_shared=False)
        assert v.seat_layout == "5"
        assert v.rudder == "1"

    def test_seat_layout_string(self) -> None:
        data: dict[str, Any] = {
            "vin": "V",
            "carType": "T03",
            "carId": 1,
            "seatLayout": "5",
            "rudder": "left",
        }
        v = Vehicle.from_dict(data, is_shared=False)
        assert v.seat_layout == "5"
        assert v.rudder == "left"

    def test_shared_fields(self) -> None:
        data: dict[str, Any] = {
            "vin": "V",
            "carType": "C10",
            "carId": 1,
            "shareTime": 1700000000,
            "expireTime": 1700100000,
            "durationType": 2,
        }
        v = Vehicle.from_dict(data, is_shared=True)
        assert v.share_time == 1700000000
        assert v.expire_time == 1700100000
        assert v.duration_type == 2

    def test_allocation_code(self) -> None:
        data: dict[str, Any] = {
            "vin": "V",
            "carType": "C10",
            "carId": 1,
            "allocationCode": "ABC123",
        }
        v = Vehicle.from_dict(data, is_shared=False)
        assert v.allocation_code == "ABC123"


# ---------------------------------------------------------------------------
# RemoteActionCtl subclasses
# ---------------------------------------------------------------------------


class TestRemoteActionCtlLock:
    def test_lock(self) -> None:
        action = RemoteActionCtlLock(value="lock")
        assert action.cmd_id == "110"
        assert action.cmd_content == '{"value":"lock"}'

    def test_unlock(self) -> None:
        action = RemoteActionCtlLock(value="unlock")
        assert action.cmd_content == '{"value":"unlock"}'


class TestRemoteActionCtlTrunk:
    def test_default(self) -> None:
        action = RemoteActionCtlTrunk()
        assert action.cmd_id == "130"
        assert action.cmd_content == '{"value":"true"}'


class TestRemoteActionCtlFindCar:
    def test_default(self) -> None:
        action = RemoteActionCtlFindCar()
        assert action.cmd_id == "120"
        assert action.cmd_content == '{"value":"true"}'


class TestRemoteActionCtlSunshade:
    def test_open(self) -> None:
        action = RemoteActionCtlSunshade(value="10")
        assert action.cmd_id == "240"
        assert action.cmd_content == '{"value":"10"}'

    def test_close(self) -> None:
        action = RemoteActionCtlSunshade(value="0")
        assert action.cmd_content == '{"value":"0"}'

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError, match="0-10"):
            RemoteActionCtlSunshade(value="11")

    def test_invalid_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="0-10"):
            RemoteActionCtlSunshade(value="-1")


class TestRemoteActionCtlBatteryPreheat:
    def test_on(self) -> None:
        action = RemoteActionCtlBatteryPreheat(value="ptcon")
        assert action.cmd_id == "160"
        assert action.cmd_content == '{"value":"ptcon"}'

    def test_off(self) -> None:
        action = RemoteActionCtlBatteryPreheat(value="ptcoff")
        assert action.cmd_content == '{"value":"ptcoff"}'


class TestRemoteActionCtlWindows:
    def test_open(self) -> None:
        action = RemoteActionCtlWindows(value="100")
        assert action.cmd_id == "230"
        assert action.cmd_content == '{"value":"100"}'

    def test_close(self) -> None:
        action = RemoteActionCtlWindows(value="0")
        assert action.cmd_content == '{"value":"0"}'

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError, match="0-100"):
            RemoteActionCtlWindows(value="101")


class TestRemoteActionCtlClimate:
    def test_default(self) -> None:
        action = RemoteActionCtlClimate()
        assert action.cmd_id == "170"
        import json

        content = json.loads(action.cmd_content)
        assert content["circle"] == "out"
        assert content["mode"] == "nohotcold"
        assert content["operate"] == "manual"
        assert content["position"] == "all"
        assert content["temperature"] == "24"
        assert content["windlevel"] == "4"
        assert content["wshld"] == "1"

    def test_custom_values(self) -> None:
        action = RemoteActionCtlClimate(
            circle="in",
            mode="cold",
            operate="auto",
            temperature="20",
            windlevel="6",
            wshld="2",
        )
        import json

        content = json.loads(action.cmd_content)
        assert content["circle"] == "in"
        assert content["mode"] == "cold"
        assert content["operate"] == "auto"
        assert content["temperature"] == "20"
        assert content["windlevel"] == "6"
        assert content["wshld"] == "2"


# ---------------------------------------------------------------------------
# StrEnum value classes
# ---------------------------------------------------------------------------


class TestEnumValues:
    def test_climate_circle(self) -> None:
        assert ClimateCircle.IN == "in"
        assert ClimateCircle.OUT == "out"

    def test_climate_mode(self) -> None:
        assert ClimateMode.COLD == "cold"
        assert ClimateMode.HOT == "hot"
        assert ClimateMode.NO_HOT_COLD == "nohotcold"

    def test_climate_operate(self) -> None:
        assert ClimateOperate.MANUAL == "manual"
        assert ClimateOperate.AUTO == "auto"

    def test_climate_position(self) -> None:
        assert ClimatePosition.ALL == "all"

    def test_climate_windshield(self) -> None:
        assert ClimateWindshield.NORMAL == "1"
        assert ClimateWindshield.DEFROST == "2"


# ---------------------------------------------------------------------------
# RemoteActionSpec & RemoteActionResult
# ---------------------------------------------------------------------------


class TestRemoteActionSpec:
    def test_fields(self) -> None:
        spec = RemoteActionSpec(cmd_id="110", cmd_content='{"value":"lock"}')
        assert spec.cmd_id == "110"
        assert spec.cmd_content == '{"value":"lock"}'


class TestRemoteActionResult:
    def test_success(self) -> None:
        r = RemoteActionResult(action="lock", success=True, data={"remoteCtlId": "abc"})
        assert r.action == "lock"
        assert r.success is True
        assert r.error is None

    def test_failure(self) -> None:
        r = RemoteActionResult(action="unlock", success=False, error="timeout")
        assert r.success is False
        assert r.error == "timeout"
        assert r.data == {}


# ---------------------------------------------------------------------------
# Message & MessageList
# ---------------------------------------------------------------------------


class TestMessage:
    def test_from_dict(self) -> None:
        data: dict[str, Any] = {
            "id": 8162044,
            "vin": "WLMTEST123456",
            "title": "Condivisione veicolo",
            "message": "Notification text",
            "sendTime": 1777029905000,
            "readFlag": 1,
            "url": '{"key":"value"}',
            "msgType": 14,
        }
        msg = Message.from_dict(data)
        assert msg.id == 8162044
        assert msg.vin == "WLMTEST123456"
        assert msg.title == "Condivisione veicolo"
        assert msg.message == "Notification text"
        assert msg.send_time == 1777029905000
        assert msg.read_flag == 1
        assert msg.url == '{"key":"value"}'
        assert msg.msg_type == 14
        assert msg.raw == data

    def test_is_read(self) -> None:
        msg = Message.from_dict({"id": 1, "readFlag": 1})
        assert msg.is_read is True

    def test_is_unread(self) -> None:
        msg = Message.from_dict({"id": 2, "readFlag": 0})
        assert msg.is_read is False

    def test_send_datetime(self) -> None:
        msg = Message.from_dict({"id": 1, "sendTime": 1700000000000})
        dt = msg.send_datetime
        assert dt is not None
        assert dt.year == 2023

    def test_send_datetime_none(self) -> None:
        msg = Message.from_dict({"id": 1})
        assert msg.send_datetime is None

    def test_missing_fields_default_none(self) -> None:
        msg = Message.from_dict({"id": 5})
        assert msg.vin is None
        assert msg.title is None
        assert msg.message is None
        assert msg.send_time is None
        assert msg.read_flag is None
        assert msg.url is None
        assert msg.msg_type is None


class TestMessageList:
    def test_from_dict(self) -> None:
        data: dict[str, Any] = {
            "count": 2,
            "list": [
                {"id": 1, "vin": "VIN1", "title": "Title1", "readFlag": 0},
                {"id": 2, "vin": "VIN2", "title": "Title2", "readFlag": 1},
            ],
        }
        ml = MessageList.from_dict(data)
        assert ml.count == 2
        assert len(ml.messages) == 2
        assert ml.messages[0].id == 1
        assert ml.messages[1].is_read is True

    def test_empty_list(self) -> None:
        ml = MessageList.from_dict({"count": 0, "list": []})
        assert ml.count == 0
        assert ml.messages == []

    def test_missing_list_key(self) -> None:
        ml = MessageList.from_dict({"count": 0})
        assert ml.messages == []
