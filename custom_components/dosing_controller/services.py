"""Services for Dosing Controller."""
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SERVICE_DOSE = "dose"

DOSE_SERVICE_SCHEMA = vol.Schema({
    vol.Optional("pump"): str,
    vol.Required("ml"): vol.Coerce(float),
})

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Dosing Controller."""
    
    async def handle_dose_service(call: ServiceCall) -> None:
        """Handle the dose service call."""
        pump_name = call.data.get("pump")
        ml = call.data["ml"]
        
        # Find the coordinator(s) to trigger
        coordinators = []
        domain_data = hass.data.get(DOMAIN, {})
        
        if pump_name:
            # Find specific pump by name
            for coordinator in domain_data.values():
                if coordinator.name == pump_name:
                    coordinators.append(coordinator)
                    break
        else:
            # Use all coordinators if no specific pump named
            coordinators = list(domain_data.values())
        
        # Trigger dose on found coordinator(s)
        for coordinator in coordinators:
            await coordinator.async_dose(ml)
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_DOSE,
        handle_dose_service,
        schema=DOSE_SERVICE_SCHEMA,
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for Dosing Controller."""
    hass.services.async_remove(DOMAIN, SERVICE_DOSE)
