# ChildSafe System


![Python](https://img.shields.io/badge/Python-3.11-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Status](https://img.shields.io/badge/status-prototype-orange)

A Python prototype of an in-vehicle child safety monitoring system.

The system simulates a smart safety unit installed in a vehicle that detects dangerous cabin conditions when a child might be left inside a locked car.

It monitors:

- Cabin temperature
- CO2 concentration
- Vehicle lock state
- Engine state

Based on these signals, the system determines whether the situation is:

- NORMAL
- WARNING
- DANGER

and triggers appropriate safety actions.

---

# Features

- Real-time condition evaluation
- Temperature danger detection (heat / cold)
- CO2 danger detection
- State machine (INACTIVE -> NORMAL -> WARNING -> DANGER)
- Automatic simulated actions:
  - open windows
  - activate AC / heating
  - trigger alarm and hazard lights
  - send mobile alert
- Simulation engine for testing different scenarios
- Webhook integration (n8n ready)
- Unit tests for core safety logic

---

# Project Structure

```text
childsafe-system
│
├── src
│   ├── engine.py
│   ├── simulator.py
│   ├── actions.py
│   ├── models.py
│   ├── state.py
│   └── config.py
│
├── tests
│   ├── test_engine_thresholds.py
│   └── test_engine_confirmation.py
│
└── .gitignore
```

---

# System Architecture

```mermaid
flowchart TD

Sensors --> Simulator
Simulator --> Engine
Engine --> StateMachine
StateMachine --> WarningActions
StateMachine --> DangerActions
DangerActions --> WebhookDispatcher
WebhookDispatcher --> n8n_system
```


# Demo

Example simulation run:

python -m src.main simulate --scenario summer

Example output:

Temperature: 42°C
CO2: 2800 ppm

State transition:
NORMAL → WARNING → DANGER

Actions triggered:
• Open windows
• Activate AC
• Trigger alarm
• Send mobile alert

This simulation demonstrates how the monitoring engine detects dangerous cabin conditions and escalates safety responses automatically.

[View architecture notes](docs/architecture.md)
```
Car Sensors
   │
   ▼
SensorEvent
   │
   ▼
MonitoringEngine
   │
   ▼
StateMachine
   │
   ├── WARNING → Warning Actions
   │
   └── DANGER → Emergency Actions
            │
            ▼
       WebhookDispatcher
            │
            ▼
           n8n
```

This architecture separates the **decision engine**, **state machine**, and **external integrations**, making the system modular and easy to test.

---

# Author

Yitzhak Ohana  
Computer Science Student – Lev Academic Center (JCT)

GitHub:  
https://github.com/itzhakohana

---

# Running the Simulation

Example:

python -m src.main simulate --scenario summer

or

python -m src.main simulate --scenario winter

You can also send alerts to a real n8n webhook:

```powershell
$env:CHILDSAFE_N8N_WEBHOOK_URL="https://your-n8n-host/webhook/childsafe"
python -m src.main simulate --scenario summer
```

To verify the webhook connection without a full simulation:

```powershell
python -m src.main test-webhook --webhook-url "https://your-n8n-host/webhook/childsafe"
```

Available webhook configuration:

- `CHILDSAFE_N8N_WEBHOOK_URL`
- `CHILDSAFE_N8N_WEBHOOK_TIMEOUT_SECONDS`
- `CHILDSAFE_N8N_WEBHOOK_SOURCE`
- `CHILDSAFE_ENABLE_N8N_WEBHOOK`

---

# Running Tests

Run all unit tests:

python -m unittest discover -s tests -v

