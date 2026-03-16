"""
ChildSafe System — Configuration
All thresholds and timing parameters are defined here.
"""

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
ENABLE_N8N_WEBHOOK = True
N8N_WEBHOOK_URL = ""
N8N_WEBHOOK_TIMEOUT_SECONDS = 5