# Dosing Controller (ESPHome + Home Assistant)

Self-contained dosing controller built on ESPHome with:
- Reusable pump package (stepper + doser + controls)
- C++ scheduler (3 schedules per pump, days of week)
- mL-first calibration workflow with Save gating
- Busy + Last Trigger indicators
- Optional Home Assistant helpers for native time pickers

No HACS integration is required.

## Setup

### ESPHome
1. Edit `esphome/dosing_controller.yaml`:
   - Set Wi‑Fi SSID/password
   - Confirm ESP32 board
   - Adjust pump pins in the `packages:` block
2. Flash: `esphome run esphome/dosing_controller.yaml`
3. First boot AP: SSID "Dosing Pump Setup" (password `pump1234`) → enter network creds.

Key files:
- `esphome/packages/pump.yaml`: pump + calibration + persistence
- `esphome/packages/schedule.yaml`: 3 schedules/pump + scheduler wiring
- `esphome/components/doser/*`: doser custom component
- `esphome/components/doser_scheduler/*`: scheduler custom component

### Home Assistant
- Helpers: use `home_assistant/doser.yaml` under `packages:` or create the same helpers manually (6 input_datetime + 4 input_boolean)
- Dashboard: paste `home_assistant/dashboard_card.yaml` into a Lovelace Manual card

Important:
- Make sure the ESPHome integration is added in Home Assistant (Settings → Devices & Services → Add Integration → ESPHome) and the dosing-controller device shows up online first.
- Only after the device is online and entities exist should you add the dashboard card, so entity IDs resolve correctly.

#### Copy `doser.yaml` into Home Assistant (helpers)
Option A — Using packages (recommended)
1) In Home Assistant, open `configuration.yaml` and ensure this exists:
   homeassistant:
     packages: !include_dir_merge_named packages
2) On the HA filesystem, create the folder and file:
   config/packages/doser.yaml
3) Open this repo file and copy its contents into HA:
   home_assistant/doser.yaml  →  config/packages/doser.yaml
4) Restart Home Assistant (Settings → System → Restart).

## How it works
- Dose in mL (device converts to step count internally)
- Calibration: Calibrate (dose target mL) → enter measured → Save (updates steps/mL once; gated to avoid compounding)
- Scheduler: 3 time slots per pump, Mon–Sun toggles, runs locally using SNTP time
- Status: `..._busy` shows motion; `..._last_trigger` shows Dose/Calibrate/Schedule N/Stopped
- Persistence: Steps‑per‑mL mirrored into a persistent global and restored on boot (survives OTA)

## Notes
- Keep IDs stable after deployment to avoid new entities and lost prefs
- Prefer the built-in helpers? We can switch to a helper‑free HH:MM text input variant on request
