#pragma once
#include "esphome.h"

namespace doser {

using namespace esphome;

class Doser : public Component {
public:
    void set_stepper(stepper::Stepper *s) { stepper_ = s; }

    void setup() override {
        ESP_LOGI("DOSER", "Doser setup complete");
    }

    void loop() override {
    }

    void calibrate(float steps, float speed) {
        if (!stepper_ || steps <= 0) return;
        if (stepper_->current_position != stepper_->target_position) {
            ESP_LOGW("DOSER", "Calibration requested while stepper is still moving; ignoring.");
            return;
        }
        stepper_->set_max_speed(speed);
        stepper_->report_position(0);
        stepper_->set_target(steps);
        ESP_LOGI("DOSER", "Starting Calibration: %d steps", steps);
    }

    void dose_ml(float ml, float steps_per_ml, float speed) {
        if (!stepper_ || ml <= 0) return;
        if (stepper_->current_position != stepper_->target_position) {
            ESP_LOGW("DOSER", "Dose requested while stepper is still moving; ignoring.");
            return;
        }
        int steps = lroundf(ml * steps_per_ml);
        stepper_->set_max_speed(speed);
        stepper_->report_position(0);
        stepper_->set_target(steps);
        ESP_LOGI("DOSER", "Starting dose: %.2f mL -> %d steps", ml, steps);
    }

    void stop() {
        if (!stepper_) return;
        stepper_->report_position(0);
        stepper_->set_target(0);
        ESP_LOGI("DOSER", "Stop requested");
    }
private:
    stepper::Stepper *stepper_{nullptr};
};
}  // namespace doser
