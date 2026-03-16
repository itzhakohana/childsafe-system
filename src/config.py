"""
ChildSafe System — Configuration
All thresholds and timing parameters are defined here.
"""

import os


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


# Temperature thresholds
TEMP_WARNING_C = 35.0
TEMP_DANGER_C = 39.0

TEMP_COLD_WARNING_C = 6.0
TEMP_COLD_DANGER_C = 2.0

# CO2 thresholds
CO2_WARNING_PPM = 1500
CO2_DANGER_PPM = 2000

# Rate-of-rise thresholds
TEMP_RATE_DANGER_C_PER_MIN = 2.0
CO2_RATE_DANGER_PPM_PER_MIN = 500.0

# Confirmation timers
CONFIRM_WARNING_SECONDS = 15
CONFIRM_DANGER_SECONDS = 20

# Moving average window
MOVING_AVG_SAMPLES = 6

# Simulation defaults
DEFAULT_STEP_SECONDS = 5
DEFAULT_DURATION_MINUTES = 10
DEFAULT_SEED = 42

# n8n webhook
ENABLE_N8N_WEBHOOK = _get_bool("CHILDSAFE_ENABLE_N8N_WEBHOOK", True)
N8N_WEBHOOK_URL = os.getenv("CHILDSAFE_N8N_WEBHOOK_URL", "").strip()
N8N_WEBHOOK_TIMEOUT_SECONDS = _get_int("CHILDSAFE_N8N_WEBHOOK_TIMEOUT_SECONDS", 5)
N8N_WEBHOOK_SOURCE = (
    os.getenv("CHILDSAFE_N8N_WEBHOOK_SOURCE", "childsafe-prototype").strip()
    or "childsafe-prototype"
)
