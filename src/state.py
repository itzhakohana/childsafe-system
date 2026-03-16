"""
ChildSafe System — State Machine
Manages state transitions and confirmation-timer logic.
"""
from __future__ import annotations
from typing import Optional

from src.models import SystemState
from src import config


class StateMachine:
    """
    Explicit finite-state machine for the ChildSafe engine.
    """

    def __init__(self) -> None:
        self._state: SystemState = SystemState.INACTIVE

        # timers
        self._warning_condition_since: Optional[int] = None
        self._danger_condition_since: Optional[int] = None

        # action gates
        self.warning_action_fired: bool = False
        self.danger_action_fired: bool = False

    @property
    def state(self) -> SystemState:
        return self._state

    def update(
        self,
        timestamp_sec: int,
        is_active: bool,
        warning_condition: bool,
        danger_condition: bool,
    ) -> tuple[SystemState, bool]:

        old_state = self._state

        if not is_active:
            new_state = self._handle_inactive()

        elif danger_condition:
            new_state = self._handle_danger(timestamp_sec)

        elif warning_condition:
            new_state = self._handle_warning(timestamp_sec)

        else:
            new_state = self._handle_normal()

        self._state = new_state
        return new_state, new_state != old_state

    def _handle_inactive(self) -> SystemState:
        self._warning_condition_since = None
        self._danger_condition_since = None
        self.warning_action_fired = False
        self.danger_action_fired = False
        return SystemState.INACTIVE

    def _handle_normal(self) -> SystemState:
        self._warning_condition_since = None
        self._danger_condition_since = None
        self.warning_action_fired = False
        self.danger_action_fired = False
        return SystemState.NORMAL

    def _handle_warning(self, timestamp_sec: int) -> SystemState:

        self._danger_condition_since = None
        self.danger_action_fired = False

        if self._warning_condition_since is None:
            self._warning_condition_since = timestamp_sec

        elapsed = timestamp_sec - self._warning_condition_since

        if elapsed >= config.CONFIRM_WARNING_SECONDS:
            return SystemState.WARNING

        return SystemState.NORMAL 

    def _handle_danger(self, timestamp_sec: int) -> SystemState:

        if self._warning_condition_since is None:
            self._warning_condition_since = timestamp_sec

        if self._danger_condition_since is None:
            self._danger_condition_since = timestamp_sec

        elapsed_danger = timestamp_sec - self._danger_condition_since

        if elapsed_danger >= config.CONFIRM_DANGER_SECONDS:
            return SystemState.DANGER

        elapsed_warning = timestamp_sec - self._warning_condition_since

        if elapsed_warning >= config.CONFIRM_WARNING_SECONDS:
            return SystemState.WARNING

        return SystemState.NORMAL

    def should_fire_warning_action(self) -> bool:

        if self._state == SystemState.WARNING and not self.warning_action_fired:
            self.warning_action_fired = True
            return True

        return False

    def should_fire_danger_action(self) -> bool:

        if self._state == SystemState.DANGER and not self.danger_action_fired:
            self.danger_action_fired = True
            return True

        return False