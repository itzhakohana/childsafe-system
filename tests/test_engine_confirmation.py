import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from src.models import SensorEvent, SystemState
from src.engine import MonitoringEngine
from src import config


def _locked_event(ts: int, temp: float, co2: int) -> SensorEvent:
    return SensorEvent(
        timestamp_sec=ts,
        car_locked=True,
        engine_on=False,
        cabin_temp_c=temp,
        co2_ppm=co2,
    )


def _inactive_event(ts: int) -> SensorEvent:
    return SensorEvent(
        timestamp_sec=ts,
        car_locked=True,
        engine_on=True,
        cabin_temp_c=25.0,
        co2_ppm=600,
    )


class TestWarningConfirmation(unittest.TestCase):

    def setUp(self):
        self.engine = MonitoringEngine()

    def _run_warning_events(self, start_ts: int, count: int, step: int = 5):
        results = []
        temp = config.TEMP_WARNING_C + 1.0
        for i in range(count):
            ts = start_ts + i * step
            result = self.engine.tick(_locked_event(ts, temp, 800))
            results.append(result)
        return results

    def test_no_warning_before_confirmation_time(self):
        steps_before = config.CONFIRM_WARNING_SECONDS // 5 - 1
        results = self._run_warning_events(0, steps_before)
        for r in results:
            self.assertNotIn(
                r.state,
                (SystemState.WARNING, SystemState.DANGER),
            )

    def test_warning_triggers_at_confirmation_time(self):
        steps_needed = config.CONFIRM_WARNING_SECONDS // 5 + 1
        results = self._run_warning_events(0, steps_needed)
        final_states = [r.state for r in results]
        self.assertIn(SystemState.WARNING, final_states)

    def test_warning_action_fires_once(self):
        steps = (config.CONFIRM_WARNING_SECONDS // 5) + 5
        results = self._run_warning_events(0, steps)
        warning_action_events = [r for r in results if "WARNING_ACTIONS" in r.actions_fired]
        self.assertEqual(len(warning_action_events), 1)


class TestDangerConfirmation(unittest.TestCase):

    def setUp(self):
        self.engine = MonitoringEngine()

    def _run_danger_events(self, start_ts: int, count: int, step: int = 5):
        results = []
        temp = config.TEMP_DANGER_C + 1.0
        for i in range(count):
            ts = start_ts + i * step
            result = self.engine.tick(_locked_event(ts, temp, 800))
            results.append(result)
        return results

    def test_no_danger_before_confirmation_time(self):
        steps_before = (config.CONFIRM_DANGER_SECONDS // 5) - 1
        results = self._run_danger_events(0, steps_before)
        for r in results:
            self.assertNotEqual(r.state, SystemState.DANGER)

    def test_danger_triggers_at_confirmation_time(self):
        steps = (config.CONFIRM_DANGER_SECONDS // 5) + 2
        results = self._run_danger_events(0, steps)
        final_states = [r.state for r in results]
        self.assertIn(SystemState.DANGER, final_states)

    def test_danger_action_fires_once(self):
        steps = (config.CONFIRM_DANGER_SECONDS // 5) + 6
        results = self._run_danger_events(0, steps)
        danger_action_events = [r for r in results if "DANGER_ACTIONS" in r.actions_fired]
        self.assertEqual(len(danger_action_events), 1)

    def test_co2_danger_confirmation(self):
        results = []
        for i in range(20):
            ts = i * 5
            result = self.engine.tick(_locked_event(ts, 25.0, config.CO2_DANGER_PPM + 100))
            results.append(result)
        final_states = [r.state for r in results]
        self.assertIn(SystemState.DANGER, final_states)


class TestInactivePreventsActions(unittest.TestCase):

    def setUp(self):
        self.engine = MonitoringEngine()

    def test_inactive_event_does_not_trigger_warning(self):
        for i in range(30):
            ev = SensorEvent(
                timestamp_sec=i * 5,
                car_locked=True,
                engine_on=True,
                cabin_temp_c=50.0,
                co2_ppm=5000,
            )
            result = self.engine.tick(ev)
            self.assertEqual(result.state, SystemState.INACTIVE)
            self.assertEqual(result.actions_fired, [])

    def test_unlocked_event_does_not_trigger_danger(self):
        for i in range(30):
            ev = SensorEvent(
                timestamp_sec=i * 5,
                car_locked=False,
                engine_on=False,
                cabin_temp_c=50.0,
                co2_ppm=5000,
            )
            result = self.engine.tick(ev)
            self.assertEqual(result.state, SystemState.INACTIVE)
            self.assertEqual(result.actions_fired, [])

    def test_inactive_clears_confirmation_timer(self):
        temp = config.TEMP_WARNING_C + 1.0

        for i in range(2):
            self.engine.tick(_locked_event(i * 5, temp, 800))

        for i in range(5):
            self.engine.tick(_inactive_event(10 + i * 5))

        ev = _locked_event(40, temp, 800)

      

        result = self.engine.tick(ev)

       

        self.assertEqual(result.state, SystemState.NORMAL)
if __name__ == "__main__":
    unittest.main()