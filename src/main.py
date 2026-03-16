"""
ChildSafe System — CLI Entry Point
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.simulator import generate_scenario
from src.io_csv import parse_csv, write_csv
from src.engine import MonitoringEngine
from src.actions import execute_actions
from src.integrations import WebhookDispatcher, build_test_payload, send_n8n_event
from src.models import SystemState


RESET = "\033[0m"
STATE_COLORS = {
    SystemState.INACTIVE: "\033[90m",
    SystemState.NORMAL: "\033[92m",
    SystemState.WARNING: "\033[93m",
    SystemState.DANGER: "\033[91m",
}


def colorize_state(state: SystemState) -> str:

    color = STATE_COLORS.get(state, "")
    if not color:
        return f"{state.value:<8}"
    return f"{color}{state.value:<8}{RESET}"


def format_time_label(timestamp_sec: int) -> str:

    minutes, seconds = divmod(timestamp_sec, 60)
    return f"{minutes:02d}:{seconds:02d}"


def format_reasons(result) -> str:

    if not result.reasons:
        return "No active risk signals."

    return "; ".join(result.reasons)


def print_event_line(result):

    ev = result.enriched.event

    print(
        f"[{format_time_label(ev.timestamp_sec)}] "
        f"{colorize_state(result.state)} | "
        f"Temp {ev.cabin_temp_c:.1f} C | "
        f"CO2 {ev.co2_ppm} ppm"
    )
    print(f"           Signals: {format_reasons(result)}")


def should_print_event(result, previous_state, step_index: int) -> bool:

    if result.state_changed:
        return True

    if result.actions_fired:
        return True

    if step_index == 0:
        return True

    if previous_state != result.state:
        return True

    if result.state in {SystemState.WARNING, SystemState.DANGER} and step_index % 6 == 0:
        return True

    if result.reasons and result.state == SystemState.NORMAL and step_index % 12 == 0:
        return True

    return False


def print_run_header():

    print("=" * 54)
    print("ChildSafe Simulation Monitor")
    print("=" * 54)


def print_run_summary(total_events: int, final_state: SystemState, action_count: int):

    print("-" * 54)
    print(
        f"Run complete | Samples: {total_events} | "
        f"Final state: {final_state.value} | Actions triggered: {action_count}"
    )


def run_events(events, disable_webhook: bool, webhook_url=None, webhook_timeout=None):

    engine = MonitoringEngine()
    dispatcher = WebhookDispatcher(
        disable_webhook=disable_webhook,
        webhook_url=webhook_url,
        webhook_timeout=webhook_timeout,
    )
    previous_state = None
    action_count = 0

    print_run_header()

    for step_index, ev in enumerate(events):

        result = engine.tick(ev)
        actions = execute_actions(result)

        if should_print_event(result, previous_state, step_index):
            print_event_line(result)

            for a in actions:
                action_text = a.detail.replace("[SIM] ", "")
                print(f"           Action : {action_text}")

            if result.state_changed:
                print(f"           Change : State entered {result.state.value}")

        action_count += len(actions)
        previous_state = result.state

        dispatcher.dispatch(result)

    if events:
        print_run_summary(len(events), previous_state, action_count)


def cmd_simulate(args):

    events = generate_scenario(
        scenario=args.scenario,
        seed=args.seed,
        step_seconds=args.step_seconds,
        duration_minutes=args.duration_minutes,
    )

    if args.output_csv:
        write_csv(events, args.output_csv)

    run_events(
        events,
        args.disable_webhook,
        webhook_url=args.webhook_url,
        webhook_timeout=args.webhook_timeout,
    )


def cmd_replay(args):

    events = parse_csv(args.input)

    run_events(
        events,
        args.disable_webhook,
        webhook_url=args.webhook_url,
        webhook_timeout=args.webhook_timeout,
    )


def cmd_test_webhook(args):

    payload = build_test_payload()
    success = send_n8n_event(
        payload,
        webhook_url=args.webhook_url,
        timeout=args.webhook_timeout,
    )

    if not success:
        raise SystemExit(1)


def add_webhook_arguments(parser):

    parser.add_argument("--disable-webhook", action="store_true")
    parser.add_argument("--webhook-url")
    parser.add_argument("--webhook-timeout", type=int)


def build_parser():

    parser = argparse.ArgumentParser(
        prog="childsafe",
        description="ChildSafe Sensor Monitoring Prototype",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sim = sub.add_parser("simulate")

    sim.add_argument(
        "--scenario",
        choices=["summer", "winter", "forgotten_child_hot_day"],
        required=True,
    )

    sim.add_argument("--seed", type=int, default=42)

    sim.add_argument("--step-seconds", type=int, default=5)

    sim.add_argument("--duration-minutes", type=int, default=10)

    sim.add_argument("--output-csv", type=Path)

    add_webhook_arguments(sim)

    sim.set_defaults(func=cmd_simulate)

    rep = sub.add_parser("replay")

    rep.add_argument("--input", required=True)

    add_webhook_arguments(rep)

    rep.set_defaults(func=cmd_replay)

    test_webhook = sub.add_parser("test-webhook")

    test_webhook.add_argument("--webhook-url")
    test_webhook.add_argument("--webhook-timeout", type=int)

    test_webhook.set_defaults(func=cmd_test_webhook)

    return parser

def main():

    parser = build_parser()

    if len(sys.argv) == 1:
        args = parser.parse_args(["simulate", "--scenario", "summer"])
    else:
        args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":

    main()
