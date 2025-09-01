from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN, CONF_NAME, CONF_DOSE_NUMBER, CONF_DOSE_BUTTON, CONF_ENABLED,
    CONF_SCHEDULE, CONF_TIME, CONF_ML, CONF_WEEKDAYS, WEEKDAY_KEYS
)

class DosingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            title = user_input[CONF_NAME]
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_DOSE_NUMBER): selector({"entity": {"domain": "number"}}),
            vol.Required(CONF_DOSE_BUTTON): selector({"entity": {"domain": "button"}}),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input=None) -> FlowResult:
        # (optional) support YAML import if you add one later
        return await self.async_step_user(user_input)

class DosingOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            # Build schedule list from rows present in user_input
            schedule = []
            for i in range(1, 7):  # up to 6 rows
                t = user_input.get(f"row{i}_time")
                ml = user_input.get(f"row{i}_ml")
                days = user_input.get(f"row{i}_weekdays")
                if t and ml not in (None, ""):
                    schedule.append({CONF_TIME: t, CONF_ML: float(ml),
                                     CONF_WEEKDAYS: days or WEEKDAY_KEYS})
            opts = {
                CONF_ENABLED: user_input.get(CONF_ENABLED, True),
                CONF_SCHEDULE: schedule,
            }
            return self.async_create_entry(title="", data=opts)

        # Defaults from existing options
        opts = {**self.entry.options}
        enabled_def = opts.get(CONF_ENABLED, True)
        sched = opts.get(CONF_SCHEDULE, [])
        def _row_def(idx, key):
            try:
                return sched[idx].get(key)
            except IndexError:
                return None

        weekday_selector = selector({"select": {"options": WEEKDAY_KEYS, "multiple": True}})
        number_selector = selector({"number": {"min": 0, "max": 999, "step": 0.1, "mode": "box"}})
        time_selector = selector({"time": {}})

        schema_dict = {
            vol.Required(CONF_ENABLED, default=enabled_def): selector({"boolean": {}})
        }
        # Build 6 editable rows
        for i in range(1, 7):
            schema_dict[vol.Optional(f"row{i}_time", default=_row_def(i-1, CONF_TIME))] = time_selector
            schema_dict[vol.Optional(f"row{i}_ml", default=_row_def(i-1, CONF_ML))] = number_selector
            schema_dict[vol.Optional(f"row{i}_weekdays",
                                     default=_row_def(i-1, CONF_WEEKDAYS) or WEEKDAY_KEYS)] = weekday_selector

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict))

async def async_get_options_flow(config_entry):
    return DosingOptionsFlow(config_entry)
