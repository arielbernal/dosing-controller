from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er
from .const import DOMAIN

class DosingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            pump_key = user_input["pump"]  # This is the full entity name without "number."
            
            # The number entity is easy - just add "number." prefix
            dose_number = f"number.{pump_key}"
            
            # Extract pump number for button matching
            pump_number = None
            if "pump1" in pump_key:
                pump_number = "1"
            elif "pump2" in pump_key:
                pump_number = "2"
            
            # Find the matching button entity
            entity_registry = er.async_get(self.hass)
            dose_button = None
            
            for entity in entity_registry.entities.values():
                if (entity.entity_id.startswith("button.") and 
                    ("dose" in entity.entity_id.lower() or 
                     (entity.original_name and "dose" in entity.original_name.lower()))):
                    button_id = entity.entity_id
                    button_name = entity.original_name or ""
                    
                    if (f"pump{pump_number}" in button_id.lower() or 
                        f"pump_{pump_number}" in button_id.lower() or
                        f"Pump {pump_number}" in button_name or
                        f"pump{pump_number}" in button_name.lower()):
                        dose_button = button_id
                        break
            
            data = {
                "name": f"Pump {pump_number}" if pump_number else pump_key.replace("_", " ").title(),
                "dose_number_entity_id": dose_number,
                "dose_button_entity_id": dose_button,
            }
            
            return self.async_create_entry(title=data["name"], data=data)

        # Auto-discover ESPHome doser pumps
        pumps = await self._discover_pumps()
        
        if not pumps:
            errors["base"] = "no_pumps_found"
        
        schema = vol.Schema({
            vol.Required("pump"): vol.In(pumps) if pumps else vol.In({}),
        })
        
        return self.async_show_form(
            step_id="user", 
            data_schema=schema, 
            errors=errors,
            description_placeholders={
                "pump_count": str(len(pumps))
            }
        )

    async def _discover_pumps(self):
        """Discover ESPHome doser pumps automatically."""
        entity_registry = er.async_get(self.hass)
        pumps = {}
        
        # Find all number entities that contain "dose" and "ml"
        dose_numbers = []
        for entity in entity_registry.entities.values():
            if (entity.entity_id.startswith("number.") and 
                "dose" in entity.entity_id.lower() and 
                "ml" in entity.entity_id.lower()):
                dose_numbers.append(entity)
        
        # Find all button entities that contain "dose"
        dose_buttons = []
        for entity in entity_registry.entities.values():
            if (entity.entity_id.startswith("button.") and 
                ("dose" in entity.entity_id.lower() or 
                 (entity.original_name and "dose" in entity.original_name.lower()))):
                dose_buttons.append(entity)
        
        # Try to match number and button entities
        for number_entity in dose_numbers:
            number_id = number_entity.entity_id
            
            # Extract pump number from entity ID
            pump_number = None
            if "pump1" in number_id:
                pump_number = "1"
            elif "pump2" in number_id:
                pump_number = "2"
            elif "_1_" in number_id or number_id.endswith("_1"):
                pump_number = "1"
            elif "_2_" in number_id or number_id.endswith("_2"):
                pump_number = "2"
            
            if pump_number:
                # Look for matching button
                button_found = None
                
                # Try multiple button patterns
                for button_entity in dose_buttons:
                    button_id = button_entity.entity_id
                    button_name = button_entity.original_name or ""
                    
                    if (f"pump{pump_number}" in button_id.lower() or 
                        f"pump_{pump_number}" in button_id.lower() or
                        f"Pump {pump_number}" in button_name or
                        f"pump{pump_number}" in button_name.lower()):
                        button_found = button_entity.entity_id
                        break
                
                if button_found:
                    # Use the full entity ID without number. prefix as the key
                    pump_key = number_id.replace("number.", "")
                    display_name = f"Pump {pump_number}"
                    pumps[pump_key] = f"{display_name} ({number_id})"
        
        return pumps

async def async_get_options_flow(config_entry):
    return DosingOptionsFlow(config_entry)

class DosingOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options for dosing schedules."""
        if user_input is not None:
            # Convert the flat form data into the schedule format
            schedule = []
            for i in range(1, 7):  # Support up to 6 dosing schedules
                time_key = f"row{i}_time"
                ml_key = f"row{i}_ml"
                weekdays_key = f"row{i}_weekdays"
                
                if (time_key in user_input and user_input[time_key] and 
                    ml_key in user_input and user_input[ml_key]):
                    schedule.append({
                        "time": user_input[time_key],
                        "ml": user_input[ml_key],
                        "weekdays": user_input.get(weekdays_key, [])
                    })
            
            options = {
                "enabled": user_input.get("enabled", True),
                "schedule": schedule
            }
            return self.async_create_entry(title="", data=options)

        # Get current options
        current_options = self.config_entry.options
        schedule = current_options.get("schedule", [])
        
        # Build the form schema
        schema_dict = {
            vol.Optional("enabled", default=current_options.get("enabled", True)): bool,
        }
        
        # Add schedule rows
        for i in range(1, 7):
            row_data = schedule[i-1] if i-1 < len(schedule) else {}
            schema_dict.update({
                vol.Optional(f"row{i}_time", default=row_data.get("time", "")): str,
                vol.Optional(f"row{i}_ml", default=row_data.get("ml", "")): vol.Coerce(float),
                vol.Optional(f"row{i}_weekdays", default=row_data.get("weekdays", [])): 
                    selector({"select": {"options": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], "multiple": True}})
            })

        return self.async_show_form(
            step_id="init", 
            data_schema=vol.Schema(schema_dict)
        )
