import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID
from esphome.components import number, switch, time, text_sensor, globals

# Reuse Doser class from the existing custom component
from ..doser import Doser

AUTO_LOAD = ["number", "switch", "time"]
MULTI_CONF = True

doser_ns = cg.global_ns.namespace("doser")
DoserScheduler = doser_ns.class_("DoserScheduler", cg.Component)

CONF_DOSER_ID = "doser_id"
CONF_TIME_ID = "time_id"
CONF_STEPS_PER_ML = "steps_per_ml"
CONF_SPEED = "speed"
CONF_SCHEDULES = "schedules"
CONF_LAST_TRIGGER = "last_trigger"
CONF_DAILY_TOTAL_GLOBAL = "daily_total_global"
CONF_LAST_RESET_DAY_GLOBAL = "last_reset_day_global"

SCHEDULE_SCHEMA = cv.Schema(
    {
        cv.Required("ml"): cv.use_id(number.Number),
        cv.Required("hour"): cv.use_id(number.Number),
        cv.Required("minute"): cv.use_id(number.Number),
        cv.Required("enabled"): cv.use_id(switch.Switch),
        cv.Required("mon"): cv.use_id(switch.Switch),
        cv.Required("tue"): cv.use_id(switch.Switch),
        cv.Required("wed"): cv.use_id(switch.Switch),
        cv.Required("thu"): cv.use_id(switch.Switch),
        cv.Required("fri"): cv.use_id(switch.Switch),
        cv.Required("sat"): cv.use_id(switch.Switch),
        cv.Required("sun"): cv.use_id(switch.Switch),
    }
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(DoserScheduler),
        cv.Required(CONF_DOSER_ID): cv.use_id(Doser),
        cv.Required(CONF_TIME_ID): cv.use_id(time.RealTimeClock),
        cv.Required(CONF_STEPS_PER_ML): cv.use_id(number.Number),
        cv.Required(CONF_SPEED): cv.use_id(number.Number),
        cv.Required(CONF_SCHEDULES): cv.All(cv.ensure_list(SCHEDULE_SCHEMA), cv.Length(min=1, max=3)),
        cv.Optional(CONF_LAST_TRIGGER): cv.use_id(text_sensor.TextSensor),
        # Accept base globals component; values may still be restored via restore_value
        cv.Optional(CONF_DAILY_TOTAL_GLOBAL): cv.use_id(globals.GlobalsComponent),
        cv.Optional(CONF_LAST_RESET_DAY_GLOBAL): cv.use_id(globals.GlobalsComponent),
    }
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    doser = await cg.get_variable(config[CONF_DOSER_ID])
    cg.add(var.set_doser(doser))

    t = await cg.get_variable(config[CONF_TIME_ID])
    cg.add(var.set_time(t))

    spm = await cg.get_variable(config[CONF_STEPS_PER_ML])
    cg.add(var.set_steps_per_ml(spm))

    speed = await cg.get_variable(config[CONF_SPEED])
    cg.add(var.set_speed(speed))

    for sch in config[CONF_SCHEDULES]:
        ml = await cg.get_variable(sch["ml"])
        hour = await cg.get_variable(sch["hour"])
        minute = await cg.get_variable(sch["minute"])
        enabled = await cg.get_variable(sch["enabled"])
        mon = await cg.get_variable(sch["mon"])
        tue = await cg.get_variable(sch["tue"])
        wed = await cg.get_variable(sch["wed"])
        thu = await cg.get_variable(sch["thu"])
        fri = await cg.get_variable(sch["fri"])
        sat = await cg.get_variable(sch["sat"])
        sun = await cg.get_variable(sch["sun"])

        cg.add(var.add_schedule(ml, hour, minute, enabled, mon, tue, wed, thu, fri, sat, sun))

    if CONF_LAST_TRIGGER in config:
        lt = await cg.get_variable(config[CONF_LAST_TRIGGER])
        cg.add(var.set_last_trigger(lt))

    if CONF_DAILY_TOTAL_GLOBAL in config:
        dt = await cg.get_variable(config[CONF_DAILY_TOTAL_GLOBAL])
        cg.add(var.set_daily_total_global(dt))

    if CONF_LAST_RESET_DAY_GLOBAL in config:
        lrd = await cg.get_variable(config[CONF_LAST_RESET_DAY_GLOBAL])
        cg.add(var.set_last_reset_day_global(lrd))
