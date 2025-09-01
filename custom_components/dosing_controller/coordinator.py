from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, time as dtime
from typing import Callable, Iterable, List

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.util import dt as dt_util

from .const import (
    CONF_DOSE_BUTTON, CONF_DOSE_NUMBER, CONF_ENABLED, CONF_ML, CONF_SCHEDULE,
    CONF_TIME, CONF_WEEKDAYS, DOMAIN, WEEKDAY_KEYS, CONF_NAME
)

@dataclass
class _Unsub:
    fn: Callable[[], None]

class DosingCoordinator:
    """Schedules and triggers doses for a single pump (one config entry)."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self._unsubs: List[_Unsub] = []

    @property
    def name(self) -> str:
        return self.entry.title or self.entry.data.get(CONF_NAME, "Dosing Pump")

    async def async_setup(self):
        await self._reschedule_all()

    async def async_unload(self):
        self._clear_schedules()

    async def async_options_updated(self):
        self._clear_schedules()
        await self._reschedule_all()

    # ---- Core scheduling ----
    def _clear_schedules(self):
        while self._unsubs:
            self._unsubs.pop().fn()

    async def _reschedule_all(self):
        opts = {**self.entry.options}
        if not opts.get(CONF_ENABLED, True):
            return

        schedule: list[dict] = opts.get(CONF_SCHEDULE, [])
        for row in schedule:
            t = row.get(CONF_TIME)
            ml = row.get(CONF_ML)
            weekdays = row.get(CONF_WEEKDAYS, [])
            if not t or ml is None:
                continue
            await self._schedule_row(t, float(ml), weekdays)

    async def _schedule_row(self, hhmm: str, ml: float, weekdays: Iterable[str]):
        hh, mm = [int(x) for x in hhmm.split(":")]
        wdset = {w.lower() for w in weekdays} if weekdays else set(WEEKDAY_KEYS)

        def next_occ(from_dt: datetime | None = None) -> datetime:
            now = dt_util.now() if from_dt is None else from_dt
            for i in range(8):
                cand = (now + timedelta(days=i)).replace(hour=hh, minute=mm, second=0, microsecond=0)
                if cand >= now and cand.strftime("%a").lower()[:3] in wdset:
                    return cand
            return now + timedelta(days=1)

        async def run(now: datetime):
            # Trigger dose then schedule next occurrence
            await self.async_dose(ml)
            nxt = next_occ(now + timedelta(seconds=1))
            self._unsubs.append(_Unsub(async_track_point_in_time(self.hass, run, nxt)))

        first = next_occ()
        self._unsubs.append(_Unsub(async_track_point_in_time(self.hass, run, first)))

    # ---- Actuate a dose ----
    async def async_dose(self, ml: float):
        num = self.entry.data[CONF_DOSE_NUMBER]
        btn = self.entry.data[CONF_DOSE_BUTTON]
        # 1) set the target ml
        await self.hass.services.async_call(
            "number", "set_value",
            {"entity_id": num, "value": ml},
            blocking=True
        )
        # 2) press the dose button
        await self.hass.services.async_call(
            "button", "press",
            {"entity_id": btn},
            blocking=False
        )
