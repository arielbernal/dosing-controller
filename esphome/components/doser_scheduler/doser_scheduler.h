#pragma once

#include "esphome.h"
#include "esphome/components/time/real_time_clock.h"
#include "esphome/components/number/number.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include <string>

namespace doser {

class Doser; // forward

class DoserScheduler : public esphome::Component {
 public:
  void set_doser(Doser *d) { doser_ = d; }
  void set_time(esphome::time::RealTimeClock *t) { time_ = t; }
  void set_steps_per_ml(esphome::number::Number *n) { steps_per_ml_ = n; }
  void set_speed(esphome::number::Number *n) { speed_ = n; }
  void set_last_trigger(esphome::text_sensor::TextSensor *ts) { last_trigger_ = ts; }

  void add_schedule(esphome::number::Number *ml,
                    esphome::number::Number *hour,
                    esphome::number::Number *minute,
                    esphome::switch_::Switch *enabled,
                    esphome::switch_::Switch *mon,
                    esphome::switch_::Switch *tue,
                    esphome::switch_::Switch *wed,
                    esphome::switch_::Switch *thu,
                    esphome::switch_::Switch *fri,
                    esphome::switch_::Switch *sat,
                    esphome::switch_::Switch *sun) {
    int idx = static_cast<int>(schedules_.size()) + 1;
    schedules_.push_back(Schedule{ml, hour, minute, enabled, mon, tue, wed, thu, fri, sat, sun, -1, idx});
  }

  void setup() override {
    last_checked_minute_ = -1;
    for (auto &s : schedules_) s.last_run_minute = -1;
  }

  void loop() override {
    if (time_ == nullptr || doser_ == nullptr || steps_per_ml_ == nullptr || speed_ == nullptr) return;
    auto now = time_->now();
    if (!now.is_valid()) return;

    const int current_minute = now.hour * 60 + now.minute;
    if (current_minute == last_checked_minute_) return; // only evaluate once per minute
    last_checked_minute_ = current_minute;

    // ESPHome day_of_week: 1=Mon .. 7=Sun (per docs)
    const int dow = now.day_of_week; // 1..7

    for (auto &s : schedules_) {
      if (!s.enabled->state) continue;
      const bool day_ok =
          (dow == 1 && s.mon->state) ||
          (dow == 2 && s.tue->state) ||
          (dow == 3 && s.wed->state) ||
          (dow == 4 && s.thu->state) ||
          (dow == 5 && s.fri->state) ||
          (dow == 6 && s.sat->state) ||
          (dow == 7 && s.sun->state);
      if (!day_ok) continue;

      const int sched_minute = static_cast<int>(s.hour->state) * 60 + static_cast<int>(s.minute->state);
      if (sched_minute != current_minute) continue;

      if (s.last_run_minute == current_minute) continue; // already fired this minute
      s.last_run_minute = current_minute;

      const float ml = s.ml->state;
      const float spm = steps_per_ml_->state;
      const float spd = speed_->state;
      if (ml > 0.0f && spm > 0.0f && spd > 0.0f) {
        // Will internally ignore if stepper is moving
        doser_->dose_ml(ml, spm, spd);
        ESP_LOGI("DOSER_SCHED", "Triggered scheduled dose: %.2f mL at %02d:%02d", ml, now.hour, now.minute);
        if (last_trigger_ != nullptr) {
          char buf[16];
          snprintf(buf, sizeof(buf), "Schedule %d", s.index);
          last_trigger_->publish_state(buf);
        }
      }
    }
  }

 private:
  struct Schedule {
    esphome::number::Number *ml;
    esphome::number::Number *hour;
    esphome::number::Number *minute;
    esphome::switch_::Switch *enabled;
    esphome::switch_::Switch *mon;
    esphome::switch_::Switch *tue;
    esphome::switch_::Switch *wed;
    esphome::switch_::Switch *thu;
    esphome::switch_::Switch *fri;
    esphome::switch_::Switch *sat;
    esphome::switch_::Switch *sun;
    int last_run_minute{ -1 };
    int index{ 0 };
  };

  Doser *doser_{nullptr};
  esphome::time::RealTimeClock *time_{nullptr};
  esphome::number::Number *steps_per_ml_{nullptr};
  esphome::number::Number *speed_{nullptr};
  esphome::text_sensor::TextSensor *last_trigger_{nullptr};
  std::vector<Schedule> schedules_{};
  int last_checked_minute_{ -1 };
};

}  // namespace doser
