# Leapmotor Cloud API Reference

Technical documentation of the endpoints, cryptography and remote commands
used by the `leapmotor-api` library.

> **Base URL:** `https://appgateway.leapmotor-international.de`
>
> All endpoints require **mutual TLS** (client certificate).
> Server certificates are self-signed: SSL verification is disabled by default.

---

## Table of Contents

- [Authentication](#authentication)
  - [Login](#login)
  - [Token Refresh](#token-refresh)
  - [Certificates](#certificates)
- [Cryptography and Signatures](#cryptography-and-signatures)
  - [Login Signature (SHA-256)](#login-signature-sha-256)
  - [HMAC Signature (authenticated requests)](#hmac-signature-authenticated-requests)
  - [Sign Key Derivation (HKDF)](#sign-key-derivation-hkdf)
  - [PKCS#12 Password (SM4)](#pkcs12-password-sm4)
  - [Vehicle PIN Encryption (AES-128-CBC)](#vehicle-pin-encryption-aes-128-cbc)
- [Read-Only Endpoints](#read-only-endpoints)
  - [Vehicle List](#vehicle-list)
  - [Vehicle Status](#vehicle-status)
  - [Mileage and Energy](#mileage-and-energy)
  - [Weekly Energy Consumption and Ranking](#weekly-energy-consumption-and-ranking)
  - [Last Week Energy Breakdown](#last-week-energy-breakdown)
  - [Vehicle Image](#vehicle-image)
  - [Image Package Download](#image-package-download)
  - [Message List](#message-list)
  - [Unread Message Count](#unread-message-count)
  - [Charging Daily Detail](#charging-daily-detail)
- [Remote Control Endpoints](#remote-control-endpoints)
  - [Certificate Sync](#certificate-sync)
  - [Operation PIN Verification](#operation-pin-verification)
  - [Remote Command Execution](#remote-command-execution)
  - [Result Polling](#result-polling)
- [Remote Commands](#remote-commands)
  - [Lock / Unlock (cmd_id=110)](#lock--unlock-cmd_id110)
  - [Find Car (cmd_id=120)](#find-car-cmd_id120)
  - [Trunk (cmd_id=130)](#trunk-cmd_id130)
  - [Battery Preheat (cmd_id=160)](#battery-preheat-cmd_id160)
  - [Sentry Mode (cmd_id=220)](#sentry-mode-cmd_id220)
  - [Climate (cmd_id=170)](#climate-cmd_id170)
  - [Send Destination (cmd_id=180)](#send-destination-cmd_id180)
  - [Set Charge Plan (cmd_id=190)](#set-charge-plan-cmd_id190)
  - [Unlock Charger (cmd_id=192)](#unlock-charger-cmd_id192)
  - [Start / Stop Charging (cmd_id=193)](#start--stop-charging-cmd_id193)
  - [Steering Wheel Heat (cmd_id=320)](#steering-wheel-heat-cmd_id320)
  - [Fuel Heating (cmd_id=380)](#fuel-heating-cmd_id380)
  - [Rearview Mirror Heat (cmd_id=440)](#rearview-mirror-heat-cmd_id440)
  - [Speed Limit (cmd_id=510)](#speed-limit-cmd_id510)
  - [Seat Heat (cmd_id=301)](#seat-heat-cmd_id301)
  - [Seat Ventilation (cmd_id=370)](#seat-ventilation-cmd_id370)
  - [Windows (cmd_id=230)](#windows-cmd_id230)
  - [Sunshade (cmd_id=240)](#sunshade-cmd_id240)

---

## Authentication

### Login

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/acct/v1/login` |
| **Cert** | App certificate (`app_cert.pem` + `app_key.pem`) |
| **Content-Type** | `application/x-www-form-urlencoded; charset=UTF-8` |
| **Signature** | SHA-256 (see [Login Signature](#login-signature-sha-256)) |

**Form body:**

| Parameter | Value |
|---|---|
| `email` | Username (email) |
| `password` | Account password |
| `loginMethod` | `1` |
| `policyId` | `20260204` |
| `isRecoverAcct` | `0` |

**Response (data):**

| Field | Description |
|---|---|
| `id` | User ID (used as `userId` in subsequent requests) |
| `token` | JWT access token |
| `refreshToken` | Token for refresh |
| `signIkm` | Input Key Material for HKDF |
| `signSalt` | Salt for HKDF |
| `signInfo` | Info for HKDF |
| `base64Cert` | Account certificate in PKCS#12 format, Base64-encoded |
| `uid` | UID for P12 password derivation |

After login, the `deviceId` is extracted from the JWT token payload
(`user_name.split(",")[2]`).

### Token Refresh

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/acct/v1/token/refresh` |
| **Cert** | Account certificate |
| **Signature** | HMAC-SHA256 (with `refreshToken` in body_params) |

**Form body:**

| Parameter | Value |
|---|---|
| `refreshToken` | Refresh token obtained from login |

**Response (data):**

| Field | Description |
|---|---|
| `token` | New access token |
| `refreshToken` | New refresh token |

### Certificates

The system uses **two levels of certificates**:

1. **App certificate** (`app_cert.pem`, `app_key.pem`) — Static application
   certificate, used for login and remote certificate sync.
   Not included in the repository.

2. **Account certificate** — Received in the login response as Base64
   PKCS#12 (`base64Cert`). Decoded with a derived password
   (see [PKCS#12 Password](#pkcs12-password-sm4)) and used as client cert
   for all subsequent authenticated requests.

---

## Cryptography and Signatures

### Login Signature (SHA-256)

Used **only** for the login request. The signature is a SHA-256 hash of
the concatenation of the following fields (in this order):

```
language + deviceType + deviceId + "1" + username + "0" + "1" + nonce + password + "20260204" + source + timestamp + version
```

| Field | Default value |
|---|---|
| `language` | `en-GB` |
| `deviceType` | `1` |
| `source` | `leapmotor` |
| `version` | `1.12.3` |
| `channel` | `1` |

### HMAC Signature (authenticated requests)

All requests after login use **HMAC-SHA256** with the sign key
derived via HKDF. The signature input varies by endpoint:

**Standard signature (build_signed_headers):**

The input is the concatenation of all field **values** (headers + optional
body params), sorted **alphabetically by key**:

```
acceptLanguage + channel + deviceId + deviceType + nonce + source + timestamp + version [+ vin] [+ body_params...]
```

**Car picture key signature:**

```
language + channel + deviceId + deviceId + deviceType + nonce + source + timestamp + version + vin
```

> Note: `deviceId` appears **twice**.

**Car picture package signature:**

```
language + channel + deviceId + deviceType + pictureKey + nonce + source + timestamp + version
```

**operatePassword verify signature:**

```
language + channel + deviceId + deviceType + nonce + operatePassword + source + timestamp + version + vin
```

**Remote control write signature (with PIN):**

```
language + channel + cmdContent + cmdId + deviceId + deviceType + nonce + operatePassword + source + timestamp + version + vin
```

**Remote control write signature (without PIN):**

```
language + channel + cmdContent + cmdId + deviceId + deviceType + nonce + source + timestamp + version + vin
```

**Remote control result query signature:**

```
language + channel + deviceId + deviceType + nonce + remoteCtlId + source + timestamp + version
```

### Sign Key Derivation (HKDF)

The HMAC key is derived using **HKDF-SHA256**:

| Parameter | Source |
|---|---|
| IKM (Input Key Material) | `signIkm` from login response |
| Salt | `signSalt` from login response |
| Info | `signInfo` from login response |
| Length | 32 bytes |

### PKCS#12 Password (SM4)

The password for decrypting the account PKCS#12 certificate is derived as follows:

1. `cn = MD5(account_id)` — hexadecimal hash
2. `app_input = cn + cn[::2] + uid[1::2]` — concatenation with slicing
3. `digest = SHA-256(app_input)` — binary hash (32 bytes)
4. `encoded = SM4_ECB_encrypt(digest)` — encryption with static round keys
5. `password = Base64(encoded[:12])[:15]` — first 12 bytes encoded, truncated to 15 characters

The SM4 algorithm uses pre-computed hardcoded round keys (not a dynamic key).

### Vehicle PIN Encryption (AES-128-CBC)

The operation PIN (`operatePassword`) is encrypted with **AES-128-CBC**:

1. Key and IV are derived from the session token:
   - `key = MD5(token[0:32])[8:24]` — 16 characters (128 bits)
   - `iv = MD5(token[32:64])[8:24]` — 16 characters (128 bits)
2. The PIN is padded with **PKCS#7** (128-bit block)
3. The result is encoded in **Base64**

If the token is absent or too short (< 64 chars), hardcoded fallback
values are used.

---

## Read-Only Endpoints

All read-only endpoints use:
- **Method:** POST
- **Content-Type:** `application/x-www-form-urlencoded`
- **Cert:** Account certificate
- **Signature:** HMAC-SHA256 (standard)
- **Additional headers:** `userId`, `token`

### Vehicle List

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/list` |
| **Body** | (empty) |

**Response (data):**

| Field | Type | Description |
|---|---|---|
| `bindcars` | `list` | Owned vehicles |
| `sharedcars` | `list` | Shared vehicles |

Each vehicle contains: `vin`, `carId`, `carType`, `nickName`, `vinNickname`,
`email`, `plateNumber`, `mobileNumber`, `outColor`, `year`, `abilities`,
`rightList`, `moduleRights`, `allocationCode`, `seatLayout`, `rudder`,
`shareTime`, `expireTime`, `durationType`.

### Vehicle Status

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/status/get/{car_type}` |
| **Body** | `vin={VIN}` |
| **Signature** | HMAC-SHA256 (with `vin` in the input) |

The `{car_type}` segment is the vehicle's `carType` in lowercase (e.g. `t03`,
`c10`). **B10** uses the **C10** path (`/status/get/c10`).

The response format varies by model — see [docs/vehicles.md](vehicles.md).

### Mileage and Energy

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/drivingRecord/v1/mileage/energy/detail` |
| **Body** | `vin={VIN}` |

**Response (data):**

| Field | Description |
|---|---|
| `totalmileage` | Total mileage (km) |
| `totalmileageMile` | Total mileage (miles) |
| `deliveryDays` | Days since delivery |

### Weekly Energy Consumption and Ranking

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/drivingRecord/v1/getLastNweeks100kmECAndRank` |
| **Body** | `carvin={VIN}` |
| **Signature** | HMAC-SHA256 (with `carvin` in body_params) |

**Response (data):**

| Field | Description |
|---|---|
| `rankResult.result` | Rank result code (0 = OK) |
| `rankResult.rank` | Percentile rank (e.g. `"0%"`) |
| `rankResult.hundredKmEC` | Average consumption (kWh/100 km) |
| `rankResult.hundredMiKwhEC` | Average consumption (kWh/100 mi) |
| `weeklyEC[].weekStart` | Week start date (`YYYY-MM-DD`) |
| `weeklyEC[].weekEnd` | Week end date (`YYYY-MM-DD`) |
| `weeklyEC[].hundredKmEC` | Consumption that week (kWh/100 km) |
| `weeklyEC[].hundredMiKwhEC` | Consumption that week (kWh/100 mi) |
| `weeklyEC[].xWeekStart` | Week start timestamp (ms) |
| `weeklyEC[].xWeekEnd` | Week end timestamp (ms) |

**Typed model:** `ConsumptionWeeklyRank` (contains `ConsumptionRank` + `list[WeeklyConsumption]`)

### Last Week Energy Breakdown

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/drivingRecord/v1/getLastweekEC` |
| **Body** | `endtime={epoch_s}&begintime={epoch_s}&carvin={VIN}` |
| **Signature** | HMAC-SHA256 (with `endtime`, `begintime`, `carvin` in body_params) |

The `begintime` / `endtime` parameters are Unix epoch seconds delimiting
the previous calendar week (Monday 00:00 → Sunday 23:59:59 UTC).

**Response (data):**

| Field | Description |
|---|---|
| `driverEC` | Driving energy consumption (kWh, string) |
| `acEC` | Air conditioning energy consumption (kWh, string) |
| `otherEC` | Other systems energy consumption (kWh, string) |

**Typed model:** `ConsumptionLastWeekBreakdown` (with `total_ec` computed property)

### Vehicle Image

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/carpicture/key` |
| **Body** | `deviceID={deviceId}&vin={VIN}` |
| **Signature** | Car picture variant (duplicated deviceId) |

**Response (data):**

| Field | Description |
|---|---|
| `key` | Key for the package download |
| `shareBindUrl` | CDN URL of the image |
| `whole` | Full image flag |

### Image Package Download

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/carpicture/package` |
| **Body** | `key={picture_key}` |
| **Signature** | Car picture package variant |
| **Response** | Binary (ZIP) |

### Message List

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/message/v1/list` |
| **Body** | `pageNo={n}&pageSize={n}` |
| **Signature** | HMAC-SHA256 (with `pageNo`, `pageSize` in body_params) |

### Unread Message Count

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/message/v1/unread/count` |
| **Body** | (empty) |

### Charging Daily Detail

| | |
|---|---|
| **Path** | `POST /carownerservice/charge/daily/detail/page` |
| **Content-Type** | `application/json` |
| **Signature** | HMAC-SHA256 (with `vin`, `timeZone`, `startTime`, `endTime`, `pageNum`, `pageSize` in body_params) |

**JSON body:**

| Parameter | Type | Description |
|---|---|---|
| `vin` | string | Vehicle Identification Number |
| `timeZone` | string | Timezone (e.g. `"GMT+01:00"`) |
| `startTime` | string | Start date (`"2025-01-01"`) |
| `endTime` | string | End date (`"2026-05-10"`) |
| `pageNum` | int | Page number (1-based) |
| `pageSize` | int | Items per page |

**Response (data):**

| Field | Type | Description |
|---|---|---|
| `list[].chargeGunStartTs` | long | Charge start timestamp (epoch ms) |
| `list[].chargeGunEndTs` | long | Charge end timestamp (epoch ms) |
| `list[].chargeType` | string | `"1"` = AC (normal), `"2"` = DC (fast) |
| `list[].chargeInEnergy` | float | Energy charged (kWh) |
| `list[].chargeStartLongitude` | string | Longitude |
| `list[].chargeStartLatitude` | string | Latitude |
| `list[].zone` | string | Timezone (e.g. `"GMT+01:00"`) |

---

## Remote Control Endpoints

### Certificate Sync

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/cert/sync` |
| **Body** | (empty) |
| **Cert** | **App certificate** (not account cert) |

Executed once per session before the first remote command.

### Operation PIN Verification

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/operPwd/verify` |
| **Body** | `operatePassword={encrypted_pin}&vin={VIN}` |
| **Signature** | operatePassword verify variant |
| **Cert** | Account certificate |

Must be called before every remote command that requires the PIN.

### Remote Command Execution

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/app/remote/ctl` |
| **Signature** | Remote control write variant |
| **Cert** | Account certificate |

**Body (with PIN):**

```
cmdContent={json}&vin={VIN}&cmdId={id}&operatePassword={encrypted_pin}
```

**Body (without PIN, e.g. send_destination):**

```
cmdContent={json}&vin={VIN}&cmdId={id}
```

**Response (data):**

| Field | Description |
|---|---|
| `remoteCtlId` | ID for result polling |
| `queryRemoteCtlResultTimeout` | Polling timeout (ms) |
| `queryInterval` | Polling interval (ms) |

### Result Polling

| | |
|---|---|
| **Path** | `POST /carownerservice/oversea/vehicle/v1/app/remote/ctl/result/query` |
| **Body** | `remoteCtlId={id}` |
| **Signature** | Remote control result variant |

Polling continues until `data == 1` (success) or the timeout expires.

---

## Remote Commands

### Lock / Unlock (cmd_id=110)

| Action | cmd_content |
|---|---|
| Lock | `{"value":"lock"}` |
| Unlock | `{"value":"unlock"}` |

Requires PIN.

### Find Car (cmd_id=120)

| Action | cmd_content |
|---|---|
| Find | `{"value":"true"}` |

Requires PIN. Activates horn/lights to locate the vehicle.

### Trunk (cmd_id=130)

| Action | cmd_content |
|---|---|
| Open | `{"value":"true"}` |
| Close | `{"value":"false"}` |

Requires PIN.

### Battery Preheat (cmd_id=160)

| Action | cmd_content |
|---|---|
| On | `{"value":"ptcon"}` |
| Off | `{"value":"ptcoff"}` |

Requires PIN.

### Sentry Mode (cmd_id=220)

| Action | cmd_content |
|---|---|
| On | `{"value":"1"}` |
| Off | `{"value":"0"}` |

Requires PIN. Controls the sentinel / dashcam mode.

### Climate (cmd_id=170)

All climate profiles use `cmd_id=170`. The `cmd_content` is a JSON with:

| Field | Values | Description |
|---|---|---|
| `circle` | `in`, `out` | Air recirculation |
| `mode` | `cold`, `hot`, `nohotcold` | Climate mode |
| `operate` | `manual`, `auto` | Operation mode |
| `position` | `all` | Air distribution position |
| `temperature` | `"18"` – `"32"` | Target temperature (°C) |
| `windlevel` | `"1"` – `"7"` | Fan level |
| `wshld` | `1`, `2` | 1=Normal, 2=Windshield defrost |

**Predefined profiles:**

| Action | circle | mode | temp | wind | wshld |
|---|---|---|---|---|---|
| AC Switch (off) | `out` | `nohotcold` | 24 | 4 | 1 |
| Quick Cool | `in` | `cold` | 18 | 7 | 1 |
| Quick Heat | `in` | `hot` | 32 | 7 | 1 |
| Windshield Defrost | `in` | `hot` | 32 | 7 | 2 |

Requires PIN.

### Send Destination (cmd_id=180)

| Field | Description |
|---|---|
| `address` | Text address |
| `addressname` | Point of interest name |
| `latitude` | Latitude (string) |
| `longitude` | Longitude (string) |
| `linenum` | `"0"` |

Does **not** require PIN. Uses the flow without `operatePassword`.

### Set Charge Plan (cmd_id=190)

| Field | Description |
|---|---|
| `chargeEnable` | 0 or 1 |
| `chargesoc` | Percentage limit (1-100) |
| `circulation` | Schedule recurrence |
| `cycles` | Active days (e.g. `"1,1,1,1,1,1,1"`) |
| `endtime` | Schedule end time |
| `recharge` | Recharge flag |
| `starttime` | Schedule start time |

Requires PIN. The command preserves the current charging schedule,
updating only the SOC limit.

### Unlock Charger (cmd_id=192)

| Action | cmd_content |
|---|---|
| Unlock | `{"operation":"unlock"}` |

Requires PIN. Unlocks the charging connector before unplugging.

### Start / Stop Charging (cmd_id=193)

| Action | cmd_content |
|---|---|
| Start | `{"value":"start"}` |
| Stop | `{"value":"stop"}` |

Requires PIN. Starts or stops charging when the connector is plugged in.
Available on C10/B10 models.

### Steering Wheel Heat (cmd_id=320)

| Action | cmd_content |
|---|---|
| On | `{"value":"on"}` |
| Off | `{"value":"off"}` |

Requires PIN. Enables or disables steering wheel heating.
Available on C10/B10 models.

### Fuel Heating (cmd_id=380)

| Action | cmd_content |
|---|---|
| On | `{"value":"1"}` |
| Off | `{"value":"0"}` |

Requires PIN. Enables or disables fuel heating (EREV/PHEV models).
Available on C10 fuel variant.

### Rearview Mirror Heat (cmd_id=440)

| Action | cmd_content |
|---|---|
| On | `{"value":"on"}` |
| Off | `{"value":"off"}` |

Requires PIN. Enables or disables rearview mirror heating.
Available on C10/B10 models.

### Speed Limit (cmd_id=510)

| Action | cmd_content |
|---|---|
| Set 80 km/h | `{"value":"80"}` |
| Set 120 km/h | `{"value":"120"}` |

Requires PIN. Sets a maximum speed limit (km/h). International models only.

### Seat Heat (cmd_id=301)

| Action | cmd_content |
|---|---|
| Driver seat, level 3 | `{"value":"3,3"}` |
| Left front, off | `{"value":"1,0"}` |

Requires PIN. Sets seat heating level.
Value format: `"position,level"` — position: 1=left_front, 2=copilot, 3=driver, 4=right_front, 5=left_rear, 6=right_rear; level: 0-3.

### Seat Ventilation (cmd_id=370)

| Action | cmd_content |
|---|---|
| Driver seat, level 3 | `{"value":"3,3"}` |
| Copilot, off | `{"value":"2,0"}` |

Requires PIN. Sets seat ventilation level.
Value format: same as Seat Heat — `"position,level"`.

### Windows (cmd_id=230)

| Action | cmd_content |
|---|---|
| Open (100%) | `{"value":"100"}` |
| Close (0%) | `{"value":"0"}` |
| Partial | `{"value":"0"}`–`{"value":"100"}` |

Requires PIN. The `value` represents the opening percentage.

### Sunshade (cmd_id=240)

| Action | cmd_content |
|---|---|
| Open (10) | `{"value":"10"}` |
| Close (0) | `{"value":"0"}` |
| Partial | `{"value":"0"}`–`{"value":"10"}` |

---

## Permission Reference

### VehicleRight — Remote Command Permissions (rightList)

Each remote command requires a corresponding right in the vehicle's
`rightList`. The server enforces permissions; the client performs a soft
check and logs a warning when a required right is missing.

| Code | Name | Required by cmd_id | Description |
|---|---|---|---|
| 110 | `LOCK` | 110 | Lock / Unlock doors |
| 120 | `FIND_CAR` | 120 | Find car (horn + lights) |
| 130 | `TRUNK` | 130 | Trunk open/close |
| 150 | `AUTOPARK` | — | Auto park / summon |
| 160 | `SUNROOF` | — | Sunroof control |
| 161 | `SUNSHADE` | 240 | Sunshade control |
| 170 | `CLIMATE` | 170 (ac_switch) | Climate / AC on-off |
| 171 | `QUICK_CLIMATE` | 170 (quick_cool/heat) | Quick cool / Quick heat |
| 180 | `SEND_DESTINATION` | 180 | Send destination (navigation) |
| 190 | `BATTERY_PREHEAT` | 160 | Battery preheating |
| 192 | `UNLOCK_CHARGER` | 192 | Unlock charger connector |
| 193 | `TOGGLE_CHARGE` | — | Start / stop charging |
| 220 | `SENTRY_MODE` | — | Sentry mode |
| 230 | `WINDOWS` | 230 | Windows |
| 240 | `SKYLIGHT` | — | Skylight control |
| 270 | `MUSIC` | — | Music control |
| 280 | `SEAT_ADJUST` | — | Seat adjust |
| 290 | `VIDEO` | — | Video |
| 301 | `SEAT_HEAT` | — | Seat heating |
| 320 | `STEERING_WHEEL_HEAT` | — | Steering wheel heating |
| 340 | `CHARGE_LIMIT` | 190 | Charge limit |
| 360 | `PREPARE_CAR` | — | Pre-conditioning (prepare car) |
| 361 | `PREPARE_CAR_ALARM` | — | Pre-conditioning alarm |
| 370 | `SEAT_VENTILATION` | — | Seat ventilation |
| 380 | `FUEL_HEATING` | — | Fuel heating |
| 460 | `WINDSHIELD_DEFROST` | 170 (defrost) | Windshield defrost / mirror heating |
| 510 | `SPEED_LIMIT` | — | Speed limit |

> **"—"** in the cmd_id column indicates the command is not yet implemented
> in this library (the right may appear in `rightList` for certain models).

### ModuleRight — Macro Permission Categories (moduleRights)

| Code | Name | Description |
|---|---|---|
| 100 | `BASIC` | Basic authorisation (lock/unlock) |
| 200 | `VEHICLE_CONTROL` | Vehicle control (climate, charge, quick control) |
| 300 | `VEHICLE_POSITIONING` | Vehicle positioning (GPS) |
| 400 | `MILEAGE_ENERGY` | Mileage & energy consumption |
