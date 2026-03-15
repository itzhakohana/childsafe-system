"""
ChildSafe System — Simulated Vehicle Actions
All actions here are simulated (prototype only).
"""

from __future__ import annotations
from typing import List

from src.models import ActionResult, DangerKind, EvalResult


def open_windows() -> ActionResult:
    return ActionResult(
        action_name="open_windows",
        success=True,
        detail="[SIM] Windows opened for ventilation",
    )


def activate_ventilation_or_ac() -> ActionResult:
    return ActionResult(
        action_name="activate_ventilation_ac",
        success=True,
        detail="[SIM] Air conditioning set to MAX COOL",
    )


def activate_heating() -> ActionResult:
    return ActionResult(
        action_name="activate_heating",
        success=True,
        detail="[SIM] Heating system set to MAX HEAT",
    )


def trigger_alarm_and_hazards() -> ActionResult:
    return ActionResult(
        action_name="trigger_alarm_hazards",
        success=True,
        detail="[SIM] Horn alarm and hazard lights activated",
    )


def send_mobile_alert(level: str, message: str) -> ActionResult:
    return ActionResult(
        action_name=f"mobile_alert_{level}",
        success=True,
        detail=f"[SIM] Mobile alert: {message}",
    )


def dispatch_warning_actions() -> List[ActionResult]:

    return [
        send_mobile_alert(
            level="warning",
            message="ChildSafe WARNING: Cabin conditions elevated. Please check vehicle.",
        )
    ]


def dispatch_danger_actions(danger_kind: DangerKind | None) -> List[ActionResult]:

    results: List[ActionResult] = []

    results.append(open_windows())

    results.append(trigger_alarm_and_hazards())

    if danger_kind == DangerKind.COLD:
        results.append(activate_heating())
    else:
        results.append(activate_ventilation_or_ac())

    results.append(
        send_mobile_alert(
            level="danger",
            message="ChildSafe DANGER: Immediate check required!",
        )
    )

    return results


def execute_actions(result: EvalResult) -> List[ActionResult]:

    all_results: List[ActionResult] = []

    if "WARNING_ACTIONS" in result.actions_fired:
        all_results.extend(dispatch_warning_actions())

    if "DANGER_ACTIONS" in result.actions_fired:
        all_results.extend(dispatch_danger_actions(result.danger_kind))

    return all_results