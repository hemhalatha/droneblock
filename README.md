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

# Install dependencies
pip install pymavlink
```

---

## Quick Start

```python
from droneblock.core.drone import Drone
from droneblock.actions.common import Arm, Takeoff, Land
from droneblock.mission.executor import Mission
from droneblock.safety.rules import SafetyRule, SafetyManager

# 1. Connect via Factory (Recommended)
drone = Drone.connect("udp://:14540")

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
    Takeoff(10, timeout=30.0), # Fail if takeoff takes > 30s
    Land()
])

try:
    drone.execute(mission)
except Exception as e:
    print(f"Mission failed: {e}")
finally:
    drone.close() # Clean shutdown
```

---

## Advanced: Dependency Injection

For better testability, you can inject a custom connector directly into the `Drone` constructor:

```python
from droneblock.core.drone import Drone
from droneblock.connectors.pymavlink_connector import PymavlinkConnector
from droneblock.core.events import EventEmitter

events = EventEmitter()
connector = PymavlinkConnector("udp://:14540", events)
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
   python -m droneblock.examples.sitl_demo
   ```

---

## Safety Rules Guide

Safety rules in `droneblock` evaluate continuously against live telemetry topics.

### How it works:
- **Priority**: Higher integer values are evaluated first.
- **Deterministic**: The first high-priority trigger in a tick wins, aborting the current mission action.
- **Context-Aware**: Rules have access to the full `DroneState` (GPS, Attitude, Battery, Status).

```python
# External Geofence Rule (Priority 15)
safety.add_rule(SafetyRule(
    condition=lambda s: s.vehicle_gps_position.alt_rel > 50,
    action=Land(),
    priority=15
))
```

---

## Replay & Trace Guide

The **Recorder** snapshots uORB topics and action triggers with monotonic timestamps.

### Recording:
```python
from droneblock.replay.recorder import Recorder
rec = Recorder(drone)
rec.start()
# ... mission logic ...
rec.stop("my_flight.json")
```

### Playing Back:
```python
from droneblock.replay.player import Player
player = Player("my_flight.json")
# Optional: Enable TRACE logs to see injection timing
from droneblock.core import logger
logger.set_level(logger.TRACE_LEVEL)
player.play(speedup=2.0) # Watch at 2x speed
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
