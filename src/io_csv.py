"""
ChildSafe System — CSV I/O
Robust CSV parsing with validation and writing support.
"""

from __future__ import annotations
import csv
import sys
from pathlib import Path
from typing import List, Optional

from src.models import SensorEvent


EXPECTED_COLUMNS = [
    "timestamp_sec",
    "car_locked",
    "engine_on",
    "cabin_temp_c",
    "co2_ppm",
]


COLUMN_TYPES = {
    "timestamp_sec": int,
    "car_locked": bool,
    "engine_on": bool,
    "cabin_temp_c": float,
    "co2_ppm": int,
}


class CSVParseError(Exception):
    def __init__(
        self,
        message: str,
        line_number: int,
        column: Optional[str] = None,
        expected_type: Optional[str] = None,
    ):
        self.line_number = line_number
        self.column = column
        self.expected_type = expected_type
        super().__init__(message)

    def pretty(self) -> str:
        parts = [f"  Line     : {self.line_number}"]
        if self.column:
            parts.append(f"  Column   : {self.column}")
        if self.expected_type:
            parts.append(f"  Expected : {self.expected_type}")
        parts.append(f"  Detail   : {self}")
        return "\n".join(parts)


def _parse_bool(value: str, column: str, line: int) -> bool:
    v = value.strip().lower()
    if v in ("1", "true"):
        return True
    if v in ("0", "false"):
        return False
    raise CSVParseError(
        f"Invalid boolean value '{value}'",
        line_number=line,
        column=column,
        expected_type="bool (0/1 or true/false)",
    )


def _parse_int(value: str, column: str, line: int) -> int:
    try:
        return int(value.strip())
    except ValueError:
        raise CSVParseError(
            f"Cannot convert '{value}' to integer",
            line_number=line,
            column=column,
            expected_type="int",
        )


def _parse_float(value: str, column: str, line: int) -> float:
    try:
        return float(value.strip())
    except ValueError:
        raise CSVParseError(
            f"Cannot convert '{value}' to float",
            line_number=line,
            column=column,
            expected_type="float",
        )


def parse_csv(path: str | Path) -> List[SensorEvent]:
    path = Path(path)

    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    events: List[SensorEvent] = []

    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)

            if reader.fieldnames is None:
                print("[ERROR] CSV file appears to be empty.", file=sys.stderr)
                sys.exit(1)

            actual_cols = [c.strip() for c in reader.fieldnames]
            if actual_cols != EXPECTED_COLUMNS:
                print("[ERROR] CSV column mismatch.", file=sys.stderr)
                print(f"  Expected : {EXPECTED_COLUMNS}", file=sys.stderr)
                print(f"  Got      : {actual_cols}", file=sys.stderr)
                sys.exit(1)

            for line_idx, row in enumerate(reader):
                line_number = line_idx + 2

                for col in EXPECTED_COLUMNS:
                    if col not in row or row[col].strip() == "":
                        err = CSVParseError(
                            f"Missing or empty value for column '{col}'",
                            line_number=line_number,
                            column=col,
                            expected_type=COLUMN_TYPES[col].__name__,
                        )
                        print(f"[ERROR] CSV parse failure:\n{err.pretty()}", file=sys.stderr)
                        sys.exit(1)

                try:
                    ts = _parse_int(row["timestamp_sec"], "timestamp_sec", line_number)
                    lock = _parse_bool(row["car_locked"], "car_locked", line_number)
                    eng = _parse_bool(row["engine_on"], "engine_on", line_number)
                    temp = _parse_float(row["cabin_temp_c"], "cabin_temp_c", line_number)
                    co2 = _parse_int(row["co2_ppm"], "co2_ppm", line_number)
                except CSVParseError as exc:
                    print(f"[ERROR] CSV parse failure:\n{exc.pretty()}", file=sys.stderr)
                    sys.exit(1)

                events.append(SensorEvent(
                    timestamp_sec=ts,
                    car_locked=lock,
                    engine_on=eng,
                    cabin_temp_c=temp,
                    co2_ppm=co2,
                ))

    except OSError as exc:
        print(f"[ERROR] Cannot read file: {exc}", file=sys.stderr)
        sys.exit(1)

    events.sort(key=lambda e: e.timestamp_sec)
    return events


def write_csv(events: List[SensorEvent], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        for ev in events:
            writer.writerow({
                "timestamp_sec": ev.timestamp_sec,
                "car_locked": int(ev.car_locked),
                "engine_on": int(ev.engine_on),
                "cabin_temp_c": ev.cabin_temp_c,
                "co2_ppm": ev.co2_ppm,
            })