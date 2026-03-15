import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from src.models import SensorEvent, DangerKind
from src.engine import evaluate_conditions
from src import config


def _event(temp: float, co2: int) -> SensorEvent:
    return SensorEvent(
        timestamp_sec=0,
        car_locked=True,
        engine_on=False,
        cabin_temp_c=temp,
        co2_ppm=co2,
    )


class TestHeatThresholds(unittest.TestCase):

    def test_below_all_thresholds_is_safe(self):
        warn, danger, reasons, kind = evaluate_conditions(_event(25.0, 800), 0.0, 0.0)
        self.assertFalse(warn)
        self.assertFalse(danger)
        self.assertEqual(reasons, [])
        self.assertIsNone(kind)

    def test_heat_warning_at_threshold(self):
        warn, danger, reasons, kind = evaluate_conditions(
            _event(config.TEMP_WARNING_C, 800), 0.0, 0.0
        )
        self.assertTrue(warn)
        self.assertFalse(danger)
        self.assertEqual(kind, DangerKind.HEAT)

    def test_heat_danger_at_threshold(self):
        warn, danger, reasons, kind = evaluate_conditions(
            _event(config.TEMP_DANGER_C, 800), 0.0, 0.0
        )
        self.assertTrue(danger)
        self.assertEqual(kind, DangerKind.HEAT)


class TestCO2Thresholds(unittest.TestCase):

    def test_co2_warning(self):
        warn, danger, reasons, kind = evaluate_conditions(
            _event(25.0, config.CO2_WARNING_PPM), 0.0, 0.0
        )
        self.assertTrue(warn)
        self.assertFalse(danger)
        self.assertEqual(kind, DangerKind.CO2)

    def test_co2_danger(self):
        warn, danger, reasons, kind = evaluate_conditions(
            _event(25.0, config.CO2_DANGER_PPM), 0.0, 0.0
        )
        self.assertTrue(danger)
        self.assertEqual(kind, DangerKind.CO2)


class TestColdThresholds(unittest.TestCase):

    def test_cold_warning_at_threshold(self):
        warn, danger, reasons, kind = evaluate_conditions(
            _event(config.TEMP_COLD_WARNING_C, 800), 0.0, 0.0
        )
        self.assertTrue(warn)
        self.assertFalse(danger)
        self.assertEqual(kind, DangerKind.COLD)

    def test_cold_danger_at_threshold(self):
        warn, danger, reasons, kind = evaluate_conditions(
            _event(config.TEMP_COLD_DANGER_C, 800), 0.0, 0.0
        )
        self.assertTrue(danger)
        self.assertEqual(kind, DangerKind.COLD)


if __name__ == "__main__":
    unittest.main()