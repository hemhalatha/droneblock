# droneblock v1.0

**droneblock** is a senior-architected, event-driven drone control framework for PX4 and ArduPilot. It reduces MAVLink boilerplate and enables safe, modular, and replayable mission logic for research, inspection, and delivery.

---

## Core Architecture

- **Event-Driven**: Built on an internal uORB-style bus for high-performance telemetry.
- **Backend-Agnostic**: Swappable connectors for Pymavlink, MAVSDK, and DroneKit via Dependency Injection.
- **Action Lifecycle**: Standardized `start -> tick -> complete -> abort` hooks with **built-in timeout enforcement**.
- **Priority Safety**: Context-aware safety engine that overrides mission logic deterministically.
- **Deterministic Replay**: Record flight traces to JSON and replay them offline to verify logic.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/user/droneblock.git
cd droneblock

# Install in editable mode (recommended for developers)
pip install -e .
```

---

## Quick Start

```python
from droneblock import Drone, Arm, Takeoff, Land, Mission
from droneblock.safety.rules import SafetyRule, SafetyManager

# 1. Connect via Factory (Recommended)
# The library automatically chooses Pymavlink for 'udp:' URLs
drone = Drone.connect("udp:127.0.0.1:14540")

# 2. Define Safety Rules (Priority 10 = High)
safety = SafetyManager(drone)
safety.add_rule(SafetyRule(
    condition=lambda state: state.battery_status.remaining_pct < 20,
    action=Land(),
    priority=10
))

# 3. Create and Execute Mission with Action Timeouts
mission = Mission([
    Arm(),
    Takeoff(altitude=10, timeout=30.0), # Fail if takeoff takes > 30s
    Land()
])

try:
    drone.execute(mission)
except Exception as e:
    print(f"Mission failed: {e}")
finally:
    drone.close() # Graceful shutdown
```

---

## Advanced: Dependency Injection

For custom testing or backend control, you can inject a connector directly:

```python
from droneblock import Drone, EventEmitter
from droneblock.connectors.pymavlink_connector import PymavlinkConnector

events = EventEmitter()
connector = PymavlinkConnector("udp:127.0.0.1:14540", events)
connector.connect()

drone = Drone(connector)
```

---

## SITL Demo Instructions

To run the full demonstration in simulation:

1. **Launch PX4 SITL**:
   ```bash
   make px4_sitl jmavsim
   ```
2. **Run the demo**:
   ```bash
   # Run the provided demo script directly
   python examples/sitl_demo.py
   ```

---

## Safety Rules Guide

Safety rules in `droneblock` evaluate continuously against live telemetry events.

### Features:
- **Priority-Driven**: Higher integer values are evaluated first.
- **Deterministic**: Triggers win immediately, aborting the current mission task safely.
- **State-Aware**: Rules have access to normalized `DroneState` (GPS, Attitude, Battery).

```python
# Geofence Rule (Altitude limit)
safety.add_rule(SafetyRule(
    condition=lambda s: s.vehicle_gps_position.alt_rel > 50,
    action=Land(),
    priority=15
))
```

---

## Replay & Trace Guide

The **Recorder** snapshots telemetry events and action lifecycle states with precise timestamps.

### Recording a Flight:
```python
from droneblock.replay.recorder import Recorder
rec = Recorder(drone)
rec.start()

# ... mission logic ...

rec.stop("flight_logs/mission_01.json")
```

### Offline Playback:
```python
from droneblock.replay.player import Player
from droneblock.core.logger import set_level, TRACE_LEVEL

# Enable high-resolution trace logs
set_level(TRACE_LEVEL)

player = Player("flight_logs/mission_01.json")
player.play(speedup=2.0) # Replay at 2x speed
```

---

## Module Purpose

| Module | Purpose |
| :--- | :--- |
| `core/` | Event bus, state store, unified Drone API, and Base Connector interfaces. |
| `connectors/` | Protocol implementations (Pymavlink, etc.) using Dependency Injection. |
| `actions/` | Atomic behaviors with standard lifecycle and timeout support. |
| `mission/` | Sequential execution, event emission, and error handling. |
| `safety/` | The priority-based rule engine. |
| `telemetry/` | uORB message normalization logic. |
| `replay/` | Trace recording and deterministic playback engine. |

---

## Developer Verification

To run tests:
```bash
python -m unittest discover tests
```
