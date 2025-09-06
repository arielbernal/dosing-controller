#pragma once
#include "esphome.h"
#include "esphome/components/time/real_time_clock.h"
#include "esphome/components/text_sensor/text_sensor.h"

namespace doser {

using namespace esphome;

class Doser : public Component {
public:
    void set_stepper(stepper::Stepper *s) { stepper_ = s; }

    void setup() override {
    }

    void loop() override {
    }

    void calibrate(float steps, float speed) {
        if (!stepper_ || steps <= 0) return;
        if (stepper_->current_position != stepper_->target_position) {
            return;
        }
        stepper_->set_max_speed(speed);
        stepper_->report_position(0);
        stepper_->set_target(steps);
    }

    void dose_ml(float ml, float steps_per_ml, float speed) {
        if (!stepper_ || ml <= 0) return;
        if (stepper_->current_position != stepper_->target_position) {
            return;
        }
        int steps = lroundf(ml * steps_per_ml);
        stepper_->set_max_speed(speed);
        stepper_->report_position(0);
        stepper_->set_target(steps);
        ESP_LOGI("DOSER", "Dosing %.2f mL", ml);
    }

    void dose_ml_with_trigger(float ml, float steps_per_ml, float speed, esphome::text_sensor::TextSensor *trigger_sensor, const std::string &action, esphome::time::RealTimeClock *time_comp) {
        if (!stepper_ || ml <= 0) return;
        if (stepper_->current_position != stepper_->target_position) {
            return;
        }
        int steps = lroundf(ml * steps_per_ml);
        stepper_->set_max_speed(speed);
        stepper_->report_position(0);
        stepper_->set_target(steps);
        ESP_LOGI("DOSER", "Dosing %.2f mL", ml);
        
        if (trigger_sensor != nullptr && time_comp != nullptr) {
            auto now = time_comp->now();
            if (now.is_valid()) {
                char buf[64];
                const char* months[] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
                snprintf(buf, sizeof(buf), "%s %02d %02d:%02d - %s - %.1fmL", 
                    months[now.month - 1], now.day_of_month, 
                    now.hour, now.minute, action.c_str(), ml);
                trigger_sensor->publish_state(buf);
            }
        }
    }

    void stop() {
        if (!stepper_) return;
        stepper_->report_position(0);
        stepper_->set_target(0);
    }
    bool is_busy() const {
        if (!stepper_) return false;
        return stepper_->current_position != stepper_->target_position;
    }
private:
    stepper::Stepper *stepper_{nullptr};
};
}  // namespace doser
