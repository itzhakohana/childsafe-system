"""
ChildSafe System — Utilities
Time formatting, moving-average computation, and display helpers.
"""

from __future__ import annotations
from collections import deque
from typing import Deque, List
from datetime import datetime


def format_timestamp(ts_sec: int) -> str:
    """Format seconds as readable time"""
    h = ts_sec // 3600
    m = (ts_sec % 3600) // 60
    s = ts_sec % 60
    return f"{h}:{m:02d}:{s:02d}"


def log_filename_now() -> str:
    """Return timestamp safe for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def date_tag_now() -> str:
    """Return short date tag"""
    return datetime.now().strftime("%Y%m%d")


class RateTracker:
    """
    Tracks rate of change (per minute) using sliding window
    """

    def __init__(self, max_samples: int = 6):
        self._window: Deque[tuple[int, float]] = deque(maxlen=max_samples)

    def update(self, timestamp_sec: int, value: float) -> float:
        """
        Add sample and return rate per minute
        """
        self._window.append((timestamp_sec, value))
        return self._compute_rate()

    def _compute_rate(self) -> float:

        if len(self._window) < 2:
            return 0.0

        t0, v0 = self._window[0]
        t1, v1 = self._window[-1]

        elapsed = t1 - t0

        if elapsed <= 0:
            return 0.0

        delta = v1 - v0

        return (delta / elapsed) * 60.0

    def reset(self) -> None:
        self._window.clear()

    @property
    def sample_count(self) -> int:
        return len(self._window)


def bool_flag(value: bool) -> str:
    return "1" if value else "0"


def reasons_str(reasons: List[str]) -> str:
    if not reasons:
        return "[]"
    return "[" + "; ".join(reasons) + "]"