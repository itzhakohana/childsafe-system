"""
ChildSafe System — Decision Engine
Core logic that evaluates sensor events.
"""

from __future__ import annotations
from typing import List, Optional, Tuple

from src import config
from src.models import (
    SensorEvent,
    EnrichedEvent,
    EvalResult,
    SystemState,
    DangerKind,
)

from src.state import StateMachine
from src.utils import RateTracker


def evaluate_conditions(
    event: SensorEvent,
    temp_rate: float,
    co2_rate: float,
) -> Tuple[bool, bool, List[str], Optional[DangerKind]]:

    reasons: List[str] = []
    warning_condition = False
    danger_condition = False
    dominant_kind: Optional[DangerKind] = None

    temp = event.cabin_temp_c
    co2 = event.co2_ppm

    # Heat
    if temp >= config.TEMP_DANGER_C:
        danger_condition = True
        reasons.append(f"Heat danger: {temp}")
        dominant_kind = DangerKind.HEAT

    elif temp >= config.TEMP_WARNING_C:
        warning_condition = True
        reasons.append(f"Heat warning: {temp}")
        dominant_kind = DangerKind.HEAT

    # Cold
    if temp <= config.TEMP_COLD_DANGER_C:
        danger_condition = True
        reasons.append(f"Cold danger: {temp}")

        if dominant_kind is None:
            dominant_kind = DangerKind.COLD

    elif temp <= config.TEMP_COLD_WARNING_C:
        warning_condition = True
        reasons.append(f"Cold warning: {temp}")

        if dominant_kind is None:
            dominant_kind = DangerKind.COLD

    # CO2
    if co2 >= config.CO2_DANGER_PPM:
        danger_condition = True
        reasons.append(f"CO2 danger: {co2}")

        if dominant_kind is None:
            dominant_kind = DangerKind.CO2

    elif co2 >= config.CO2_WARNING_PPM:
        warning_condition = True
        reasons.append(f"CO2 warning: {co2}")

        if dominant_kind is None:
            dominant_kind = DangerKind.CO2

    # Rate checks
    # Fast-rising signals should create an early WARNING,
    # but not trigger DANGER by themselves.
    if co2_rate >= config.CO2_RATE_DANGER_PPM_PER_MIN:
        warning_condition = True
        reasons.append("CO2 rising fast")

        if dominant_kind is None:
            dominant_kind = DangerKind.RATE

    if temp_rate >= config.TEMP_RATE_DANGER_C_PER_MIN:
        warning_condition = True
        reasons.append("Temp rising fast")

        if dominant_kind is None:
            dominant_kind = DangerKind.RATE
    if danger_condition:
        warning_condition = True

    return warning_condition, danger_condition, reasons, dominant_kind


class MonitoringEngine:

    def __init__(self) -> None:

        self.sm = StateMachine()

        self._temp_tracker = RateTracker(max_samples=config.MOVING_AVG_SAMPLES)
        self._co2_tracker = RateTracker(max_samples=config.MOVING_AVG_SAMPLES)

    def reset(self) -> None:

        self.sm = StateMachine()

        self._temp_tracker = RateTracker(max_samples=config.MOVING_AVG_SAMPLES)
        self._co2_tracker = RateTracker(max_samples=config.MOVING_AVG_SAMPLES)

    def tick(self, event: SensorEvent) -> EvalResult:

        ts = event.timestamp_sec

        temp_rate = self._temp_tracker.update(ts, event.cabin_temp_c)
        co2_rate = self._co2_tracker.update(ts, float(event.co2_ppm))

        enriched = EnrichedEvent(
            event=event,
            temp_rate_c_per_min=temp_rate,
            co2_rate_ppm_per_min=co2_rate,
        )

        if event.is_active():

            warning_cond, danger_cond, reasons, dominant_kind = evaluate_conditions(
                event,
                temp_rate,
                co2_rate,
            )

        else:

            warning_cond, danger_cond, reasons, dominant_kind = False, False, [], None

        new_state, changed = self.sm.update(
            timestamp_sec=ts,
            is_active=event.is_active(),
            warning_condition=warning_cond,
            danger_condition=danger_cond,
        )

        actions_fired: List[str] = []

        if new_state == SystemState.WARNING and self.sm.should_fire_warning_action():
            actions_fired.append("WARNING_ACTIONS")

        if new_state == SystemState.DANGER and self.sm.should_fire_danger_action():
            actions_fired.append("DANGER_ACTIONS")

        return EvalResult(
            enriched=enriched,
            state=new_state,
            reasons=reasons,
            state_changed=changed,
            actions_fired=actions_fired,
            danger_kind=dominant_kind,
        )