from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector
from .const import DOMAIN

CONF_NAME = "name"
CONF_DOSE_NUMBER = "dose_number_entity_id"
CONF_DOSE_BUTTON = "dose_button_entity_id"

class DosingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Create the config entry
            title = user_input[CONF_NAME]
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_DOSE_NUMBER): selector({"entity": {"domain": "number"}}),
            vol.Required(CONF_DOSE_BUTTON): selector({"entity": {"domain": "button"}}),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

async def async_get_options_flow(config_entry):
    return DosingOptionsFlow(config_entry)

class DosingOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        # Empty options form for now—just to prove it opens
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))
