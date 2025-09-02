from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import DosingCoordinator
from .services import async_setup_services, async_unload_services

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dosing Controller from a config entry."""
    coordinator = DosingCoordinator(hass, entry)
    await coordinator.async_setup()
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # Set up services if this is the first entry
    if len(hass.data[DOMAIN]) == 1:
        await async_setup_services(hass)
    
    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator:
        await coordinator.async_unload()
    
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    
    # Unload services if this was the last entry
    if not hass.data.get(DOMAIN):
        await async_unload_services(hass)
    
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_options_updated()
