"""
ChildSafe System — n8n Webhook Integration
Handles outbound HTTP calls to an n8n Webhook node.

Standard library only.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Optional

from src.models import EvalResult, SystemState
from src import config


def build_payload(event_type: str, result: EvalResult) -> dict:

    ev = result.enriched.event

    return {
        "source": "childsafe-prototype",
        "event_type": event_type,
        "timestamp_sec": ev.timestamp_sec,
        "state": result.state.value,
        "cabin_temp_c": ev.cabin_temp_c,
        "co2_ppm": ev.co2_ppm,
        "reasons": list(result.reasons),
        "actions_triggered": list(result.actions_fired),
    }


def send_n8n_event(
    payload: dict,
    webhook_url: Optional[str] = None,
    timeout: Optional[int] = None,
) -> bool:

    url = webhook_url if webhook_url is not None else config.N8N_WEBHOOK_URL
    timeout = timeout if timeout is not None else config.N8N_WEBHOOK_TIMEOUT_SECONDS

    if not url or not url.strip():
        print("\n[N8N] Dry-run payload:")
        print(json.dumps(payload, indent=2))
        return False

    body_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=body_bytes,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "childsafe-prototype",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.status
            if 200 <= status < 300:
                print(f"[N8N] Event sent successfully (HTTP {status})")
                return True
            else:
                print(f"[N8N] Failed to send event: HTTP {status}")
                return False

    except urllib.error.HTTPError as exc:
        print(f"[N8N] HTTP error: {exc.code} {exc.reason}")
        return False

    except urllib.error.URLError as exc:
        print(f"[N8N] Connection error: {exc.reason}")
        return False

    except Exception as exc:
        print(f"[N8N] Unexpected error: {exc}")
        return False


class WebhookDispatcher:

    _ELEVATED = frozenset({SystemState.WARNING, SystemState.DANGER})

    def __init__(self, disable_webhook: bool = False):

        self._prev_state: Optional[SystemState] = None
        self._disable_webhook = disable_webhook

        self._elevated_entry_sent = False
        self._reset_sent = False

    def dispatch(self, result: EvalResult):

        if self._disable_webhook or not config.ENABLE_N8N_WEBHOOK:
            return

        current = result.state
        prev = self._prev_state

        event_type: Optional[str] = None

        if current in self._ELEVATED and prev not in self._ELEVATED:
            self._elevated_entry_sent = False
            self._reset_sent = False

        if current == SystemState.WARNING and not self._elevated_entry_sent:

            event_type = "warning_detected"
            self._elevated_entry_sent = True

        elif current == SystemState.DANGER and prev != SystemState.DANGER:

            event_type = "danger_detected"
            self._elevated_entry_sent = True

        elif current not in self._ELEVATED and prev in self._ELEVATED and not self._reset_sent:

            event_type = "state_reset"
            self._reset_sent = True
            self._elevated_entry_sent = False

        self._prev_state = current

        if event_type is not None:

            payload = build_payload(event_type, result)
            send_n8n_event(payload)