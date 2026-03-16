"""
ChildSafe System — Scenario Simulator
Generates realistic sensor event sequences for summer and winter scenarios.
"""
from __future__ import annotations


from .car_simulation import CarEnvironment
import random
import math
from typing import List

from src.models import SensorEvent


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
def generate_forgotten_child_hot_day(
    seed: int,
    step_seconds: int,
    duration_minutes: int,
) -> List[SensorEvent]:
    """
    Simulates a dangerous hot day scenario:
    child left in a locked car, heat and CO2 gradually rise.
    """
    env = CarEnvironment(
        outside_temp_c=34.0,
        cabin_temp_c=28.0,
        co2_ppm=500,
        child_present=True,
        windows_open_pct=0,
        ac_on=False,
        heater_on=False,
        car_locked=True,
        engine_on=False,
        sunlight_factor=1.0,
    )

    events: List[SensorEvent] = []
    total_steps = (duration_minutes * 60) // step_seconds

    for i in range(total_steps):
        ts = i * step_seconds

        if i > 0:
            env.step(step_seconds)

        events.append(
            SensorEvent(
                timestamp_sec=ts,
                car_locked=env.car_locked,
                engine_on=env.engine_on,
                cabin_temp_c=round(_clamp(env.cabin_temp_c, -50.0, 80.0), 2),
                co2_ppm=max(400, int(env.co2_ppm)),
            )
        )

    return events
  

def generate_summer(
    seed: int,
    step_seconds: int,
    duration_minutes: int,
) -> List[SensorEvent]:
    rng = random.Random(seed)
    events: List[SensorEvent] = []
    total_steps = (duration_minutes * 60) // step_seconds

    for i in range(total_steps):
        ts = i * step_seconds
        elapsed_min = ts / 60.0

        phase1_end = 1.0
        phase2_end = 9.0

        if elapsed_min < phase1_end:
            engine_on = True
            car_locked = False
            temp = rng.uniform(28.0, 30.0)
            co2 = rng.randint(600, 800)

        elif elapsed_min < phase2_end:
            engine_on = False
            car_locked = True

            t = (elapsed_min - phase1_end) / (phase2_end - phase1_end)
            heat_factor = 1.0 - math.exp(-3.5 * t)
            base_temp = _lerp(29.0, 43.0, heat_factor)
            temp = base_temp + rng.gauss(0, 0.4)

            co2_factor = t ** 0.7
            base_co2 = _lerp(800, 2600, co2_factor)
            co2 = int(base_co2 + rng.gauss(0, 50))

        else:
            engine_on = False
            car_locked = False
            temp = rng.uniform(40.0, 42.0)
            co2 = rng.randint(2200, 2600)

        events.append(SensorEvent(
            timestamp_sec=ts,
            car_locked=car_locked,
            engine_on=engine_on,
            cabin_temp_c=round(_clamp(temp, -50.0, 80.0), 2),
            co2_ppm=max(400, co2),
        ))

    return events


def generate_winter(
    seed: int,
    step_seconds: int,
    duration_minutes: int,
) -> List[SensorEvent]:
    rng = random.Random(seed + 1000)
    events: List[SensorEvent] = []
    total_steps = (duration_minutes * 60) // step_seconds

    for i in range(total_steps):
        ts = i * step_seconds
        elapsed_min = ts / 60.0

        phase1_end = 1.0
        phase2_end = 9.0

        if elapsed_min < phase1_end:
            engine_on = True
            car_locked = False
            temp = rng.uniform(12.0, 15.0)
            co2 = rng.randint(600, 800)

        elif elapsed_min < phase2_end:
            engine_on = False
            car_locked = True

            t = (elapsed_min - phase1_end) / (phase2_end - phase1_end)
            cool_factor = 1.0 - math.exp(-2.8 * t)
            base_temp = _lerp(13.0, 1.0, cool_factor)
            temp = base_temp + rng.gauss(0, 0.3)

            co2_factor = t ** 0.8
            base_co2 = _lerp(800, 2100, co2_factor)
            co2 = int(base_co2 + rng.gauss(0, 45))

        else:
            engine_on = False
            car_locked = False
            temp = rng.uniform(1.0, 3.0)
            co2 = rng.randint(1900, 2200)

        events.append(SensorEvent(
            timestamp_sec=ts,
            car_locked=car_locked,
            engine_on=engine_on,
            cabin_temp_c=round(_clamp(temp, -50.0, 80.0), 2),
            co2_ppm=max(400, co2),
        ))

    return events


SCENARIOS = {
    "summer": generate_summer,
    "winter": generate_winter,
    "forgotten_child_hot_day": generate_forgotten_child_hot_day,
}


def generate_scenario(
    scenario: str,
    seed: int,
    step_seconds: int,
    duration_minutes: int,
) -> List[SensorEvent]:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario}'. Available: {list(SCENARIOS)}")
    return SCENARIOS[scenario](seed, step_seconds, duration_minutes)