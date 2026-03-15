# ChildSafe System

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