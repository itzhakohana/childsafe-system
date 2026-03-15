"""
ChildSafe System — CLI Entry Point
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.simulator import generate_scenario
from src.io_csv import parse_csv, write_csv
from src.engine import MonitoringEngine
from src.actions import execute_actions
from src.integrations import WebhookDispatcher


def print_event_line(result):

    ev = result.enriched.event

    reasons = ",".join(result.reasons) if result.reasons else "-"

    print(
        f"t={ev.timestamp_sec}s | "
        f"locked={int(ev.car_locked)} | "
        f"engine={int(ev.engine_on)} | "
        f"temp={ev.cabin_temp_c:.1f}C | "
        f"co2={ev.co2_ppm} | "
        f"state={result.state.value} | "
        f"reasons=[{reasons}]"
    )


def run_events(events, disable_webhook: bool):

    engine = MonitoringEngine()
    dispatcher = WebhookDispatcher(disable_webhook=disable_webhook)

    for ev in events:

        result = engine.tick(ev)

        print_event_line(result)

        actions = execute_actions(result)

        for a in actions:
            print(f"  ACTION: {a.action_name} -> {a.detail}")

        dispatcher.dispatch(result)


def cmd_simulate(args):

    events = generate_scenario(
        scenario=args.scenario,
        seed=args.seed,
        step_seconds=args.step_seconds,
        duration_minutes=args.duration_minutes,
    )

    if args.output_csv:
        write_csv(events, args.output_csv)

    run_events(events, args.disable_webhook)


def cmd_replay(args):

    events = parse_csv(args.input)

    run_events(events, args.disable_webhook)


def build_parser():

    parser = argparse.ArgumentParser(
        prog="childsafe",
        description="ChildSafe Sensor Monitoring Prototype",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sim = sub.add_parser("simulate")

    sim.add_argument("--scenario", choices=["summer", "winter"], required=True)

    sim.add_argument("--seed", type=int, default=42)

    sim.add_argument("--step-seconds", type=int, default=5)

    sim.add_argument("--duration-minutes", type=int, default=10)

    sim.add_argument("--output-csv", type=Path)

    sim.add_argument("--disable-webhook", action="store_true")

    sim.set_defaults(func=cmd_simulate)

    rep = sub.add_parser("replay")

    rep.add_argument("--input", required=True)

    rep.add_argument("--disable-webhook", action="store_true")

    rep.set_defaults(func=cmd_replay)

    return parser


def main():

    parser = build_parser()

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":

    main()