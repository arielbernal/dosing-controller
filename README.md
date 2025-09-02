# Dosing Controller (Home Assistant)

A custom integration for scheduling doses on ESPHome-based peristaltic pumps.

## Installation

### ESPHome Setup
1. Flash the `esphome/dosing_controller.yaml` to your ESP32
2. On first boot, connect to the "Dosing Pump Setup" WiFi network (password: pump1234)
3. Configure your WiFi credentials through the captive portal
4. The device will restart and connect to your network

### Home Assistant Integration
1. Add this repo to HACS (Integrations → ⋯ → Custom repositories)
2. Download the integration, restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration → search "Dosing Controller"
4. Configure each pump by selecting its entities from the ESPHome device

## Usage
- Configure your pump entities (Dose amount number, Dose now button).
- Open Options to add dosing times, volumes, weekdays.
- The integration handles scheduling; no automations needed.

## Services
- `dosing_controller.dose` — trigger a manual dose with:
```yaml
ml: 2.0
pump: "Pump 1"
