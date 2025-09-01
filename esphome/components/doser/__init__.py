import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import stepper
from esphome.const import CONF_ID

MULTI_CONF = True              # <-- allow a list of 'doser:' entries
AUTO_LOAD = ["stepper"]        # <-- make sure stepper is ready

doser_ns = cg.global_ns.namespace("doser")
Doser = doser_ns.class_("Doser", cg.Component)

CONF_STEPPER_ID = "stepper_id"

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(Doser),
    cv.Required(CONF_STEPPER_ID): cv.use_id(stepper.Stepper),
})

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    s = await cg.get_variable(config[CONF_STEPPER_ID])
    cg.add(var.set_stepper(s))
