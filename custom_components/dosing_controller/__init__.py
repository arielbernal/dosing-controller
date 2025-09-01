from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from .const import DOMAIN, CONF_NAME
from .coordinator import DosingCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coord = DosingCoordinator(hass, entry)
    await coord.async_setup()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coord

    async def _dose_service(call: ServiceCall):
        # Fields: pump (optional, matches entry title/name), ml (required)
        ml = float(call.data["ml"])
        pump = call.data.get("pump")
        # Run against this entry if name matches or if no pump specified.
        if pump is None or pump == (entry.title or entry.data.get(CONF_NAME)):
            await coord.async_dose(ml)

    # Register once per entry (fine — service calls are cheap)
    hass.services.async_register(DOMAIN, "dose", _dose_service)
    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, "dose"))
    entry.async_on_unload(entry.add_update_listener(_options_updated))
    return True

async def _options_updated(hass: HomeAssistant, entry: ConfigEntry):
    coord: DosingCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coord.async_options_updated()

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coord: DosingCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coord.async_unload()
    return True
