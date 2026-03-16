import os
import sys
from unittest import TestCase
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.integrations import WebhookDispatcher, build_payload, build_test_payload
from src.models import DangerKind, EnrichedEvent, EvalResult, SensorEvent, SystemState


def _result(state: SystemState, ts: int = 10, state_changed: bool = True) -> EvalResult:
    event = SensorEvent(
        timestamp_sec=ts,
        car_locked=True,
        engine_on=False,
        cabin_temp_c=38.5,
        co2_ppm=1700,
    )
    enriched = EnrichedEvent(
        event=event,
        temp_rate_c_per_min=1.4,
        co2_rate_ppm_per_min=180.0,
    )
    return EvalResult(
        enriched=enriched,
        state=state,
        reasons=["heat_warning"],
        state_changed=state_changed,
        actions_fired=["WARNING_ACTIONS"],
        danger_kind=DangerKind.HEAT,
    )


class TestBuildPayload(TestCase):

    def test_payload_contains_n8n_fields(self):
        payload = build_payload("warning_detected", _result(SystemState.WARNING))

        self.assertEqual(payload["event_type"], "warning_detected")
        self.assertEqual(payload["state"], "WARNING")
        self.assertEqual(payload["danger_kind"], "heat")
        self.assertTrue(payload["car_locked"])
        self.assertFalse(payload["engine_on"])
        self.assertEqual(payload["actions_triggered"], ["WARNING_ACTIONS"])

    def test_build_test_payload_has_expected_shape(self):
        payload = build_test_payload()

        self.assertEqual(payload["event_type"], "manual_test")
        self.assertEqual(payload["state"], "WARNING")
        self.assertIn("manual_webhook_test", payload["reasons"])


class TestWebhookDispatcher(TestCase):

    @patch("src.integrations.send_n8n_event")
    def test_warning_then_danger_then_reset_emit_expected_events(self, send_n8n_event):
        dispatcher = WebhookDispatcher(
            webhook_url="https://example.com/webhook",
            webhook_timeout=9,
        )

        dispatcher.dispatch(_result(SystemState.NORMAL, state_changed=False))
        dispatcher.dispatch(_result(SystemState.WARNING))
        dispatcher.dispatch(_result(SystemState.DANGER, ts=15))
        dispatcher.dispatch(_result(SystemState.NORMAL, ts=20))

        self.assertEqual(send_n8n_event.call_count, 3)
        first_payload = send_n8n_event.call_args_list[0].args[0]
        second_payload = send_n8n_event.call_args_list[1].args[0]
        third_payload = send_n8n_event.call_args_list[2].args[0]

        self.assertEqual(first_payload["event_type"], "warning_detected")
        self.assertEqual(second_payload["event_type"], "danger_detected")
        self.assertEqual(third_payload["event_type"], "state_reset")

        self.assertEqual(
            send_n8n_event.call_args_list[0].kwargs["webhook_url"],
            "https://example.com/webhook",
        )
        self.assertEqual(send_n8n_event.call_args_list[0].kwargs["timeout"], 9)

    @patch("src.integrations.send_n8n_event")
    def test_disabled_dispatcher_does_not_send(self, send_n8n_event):
        dispatcher = WebhookDispatcher(disable_webhook=True)
        dispatcher.dispatch(_result(SystemState.WARNING))
        send_n8n_event.assert_not_called()
