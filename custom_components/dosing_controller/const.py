DOMAIN = "dosing_controller"

CONF_NAME = "name"
CONF_DOSE_NUMBER = "dose_number_entity_id"   # number.* entity (your dose mL)
CONF_DOSE_BUTTON = "dose_button_entity_id"   # button.* entity (your 'Dose Now')

# Options
CONF_ENABLED = "enabled"
CONF_SCHEDULE = "schedule"        # list of {time:"HH:MM", ml:float, weekdays:[...]}
CONF_TIME = "time"
CONF_ML = "ml"
CONF_WEEKDAYS = "weekdays"

WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
