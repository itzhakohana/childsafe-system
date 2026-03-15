"""
ChildSafe System — Data Models
All core types: enums, dataclasses, and typed results.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional


class SystemState(Enum):
    """
    Explicit states for the ChildSafe monitoring engine.

    Priority (highest -> lowest): INACTIVE > DANGER > WARNING > NORMAL
    """
    INACTIVE = "INACTIVE"
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    DANGER = "DANGER"


class DangerKind(Enum):
    """Classifies the type of environmental danger detected."""
    HEAT = auto()
    COLD = auto()
    CO2 = auto()
    RATE = auto()


@dataclass(frozen=True)
class SensorEvent:
    """
    One discrete sensor reading.
    Exactly mirrors one CSV row.
    """
    timestamp_sec: int
    car_locked: bool
    engine_on: bool
    cabin_temp_c: float
    co2_ppm: int

    def is_active(self) -> bool:
        """System is active when locked and engine off."""
        return self.car_locked and not self.engine_on


@dataclass
class EnrichedEvent:
    """
    Sensor event augmented with moving-average derived signals.
    """
    event: SensorEvent
    temp_rate_c_per_min: float = 0.0
    co2_rate_ppm_per_min: float = 0.0

    @property
    def timestamp_sec(self) -> int:
        return self.event.timestamp_sec


@dataclass
class EvalResult:
    """
    Full output from one engine tick.
    """
    enriched: EnrichedEvent
    state: SystemState
    reasons: List[str] = field(default_factory=list)
    state_changed: bool = False
    actions_fired: List[str] = field(default_factory=list)
    danger_kind: Optional[DangerKind] = None


@dataclass
class ActionResult:
    """Structured return from a simulated vehicle action."""
    action_name: str
    success: bool
    detail: str