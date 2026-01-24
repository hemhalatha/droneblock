# DroneBlock

**DroneBlock** is a professional, event-driven Python framework for advanced drone control. It provides a high-level, standardized interface for MAVLink communication, specifically designed for PX4 and ArduPilot autonomous systems.

---

## Quick Start

### Installation
```bash
pip install droneblock
```

### Basic Implementation
The following example demonstrates a standard takeoff and landing sequence:
```python
from droneblock import Drone, Takeoff, Land

# Initialize connection to the vehicle
drone = Drone.connect("udp:127.0.0.1:14540")

# Execute mission actions
try:
    drone.execute(Takeoff(altitude=5.0))
    drone.execute(Land())
finally:
    drone.close()
```

---

## Core Features

*   **Standardized API**: Abstracts low-level MAVLink protocols into intuitive Python classes.
*   **Safety Architecture**: Priority-based safety manager for deterministic fail-safe execution.
*   **Mission Execution**: Supports both sequential and non-blocking mission orchestration.
*   **Deterministic Replay**: Provides high-resolution trace recording and offline playback for logic verification.
*   **Type Safe**: Comprehensive PEP 484 type hints for improved reliability and developer experience.

---

## Detailed Usage

### Sequential Missions
Mission sequences are managed by the `MissionExecutor` for synchronized execution:
```python
from droneblock import Drone, Arm, Takeoff, Goto, Land, Mission

mission = Mission([
    Arm(),
    Takeoff(altitude=10, timeout=30),
    Goto(lat=-35.36, lon=149.16, alt=10),
    Land()
])

drone.execute(mission)
```

### Safety Constraints
Register safety rules to handle critical vehicle states automatically:
```python
from droneblock.safety.rules import SafetyRule, SafetyManager

safety = SafetyManager(drone)
safety.add_rule(SafetyRule(
    condition=lambda state: state.battery_status.remaining_pct < 20,
    action=Land(),
    priority=10 # Higher values indicate higher priority
))
```

---

## Advanced Capabilities

<details>
<summary><b>Telemetry Recording and Playback</b></summary>

Capture flight data into standardized JSON trace files for offline analysis and logic validation.

```python
from droneblock.replay.recorder import Recorder

# Initialize and start recording
recorder = Recorder(drone)
recorder.start()

# Stop and persist trace to disk
recorder.stop("flight_log.json")

# Execute offline playback
from droneblock.replay.player import Player
Player("flight_log.json").play(speedup=2.0)
```
</details>

<details>
<summary><b>Architecture and Backend Connectors</b></summary>

DroneBlock utilizes a Factory Pattern to support multiple backend drivers:
- **Pymavlink**: Primary production backend.
- **MAVSDK**: High-performance asynchronous backend.
- **DroneKit**: Legacy support for ArduPilot systems.

The appropriate connector is automatically instantiated based on the connection URL scheme.
</details>

---

## Technical Verification

To execute the automated test suite and verify system integrity:
```bash
python -m unittest discover tests
```

---

> [!NOTE]
> For comprehensive simulation examples, refer to the scripts located in the `examples/` directory.
