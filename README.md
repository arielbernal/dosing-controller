# Dosing Controller (Home Assistant)

A custom integration for scheduling doses on ESPHome-based peristaltic pumps.

## Installation
1. Add this repo to HACS (Integrations → ⋯ → Custom repositories).
2. Download the integration, restart Home Assistant.
3. Go to Settings → Devices & Services → Add Integration → search "Dosing Controller".

## Usage
- Configure your pump entities (Dose amount number, Dose now button).
- Open Options to add dosing times, volumes, weekdays.
- The integration handles scheduling; no automations needed.

## Services
- `dosing_controller.dose` — trigger a manual dose with:
```yaml
ml: 2.0
pump: "Pump 1"
