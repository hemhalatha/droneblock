"""
DroneBlock Full SITL Demonstration
-----------------------------------
This script uses EVERY major module in the DroneBlock package to execute
a comprehensive, real-world simulation workflow.

It covers:
1. Core        -> Drone connection and Event Bus linking
2. Events      -> Custom telemetry listener callbacks
3. Safety      -> Priority-based rules and interruption (Battery/Failsafe)
4. Recording   -> High-frequency background JSON telemetry logging
5. Mission     -> Synchronous sequential execution (Arm -> Takeoff -> Goto -> Land)
6. Playback    -> Offline execution reconstruction of the recorded dictionary
"""

import time
import os
import logging
from droneblock import Drone, Arm, Takeoff, Goto, Land, Mission
from droneblock.core.logger import set_level
from droneblock.safety.rules import SafetyManager, SafetyRule
from droneblock.replay.recorder import Recorder
from droneblock.replay.player import Player


def main():
    # Hide verbose framework logs to provide a clean, demo-focused terminal output
    set_level(logging.WARNING)
    print("=== DroneBlock Full SITL Demonstration ===")

    # ---------------------------------------------------------
    # 1. Hardware Connection
    # ---------------------------------------------------------
    print("\n[1] Connecting to SITL on tcp:127.0.0.1:5762...")
    try:
        drone = Drone.connect("tcp:127.0.0.1:5762")
        print(f"Connected! Initial State: {drone.state.vehicle_status.nav_state}")
    except Exception as e:
        print(f"Failed to connect. Is your SITL running? ({e})")
        return

    # ---------------------------------------------------------
    # 2. Event Bus & Telemetry Subs
    # ---------------------------------------------------------
    print("\n[2] Registering Custom Telemetry Listeners...")

    def on_position_update(pos):
        # Only print occasionally to prevent terminal spam
        if getattr(on_position_update, "counter", 0) % 50 == 0:
            print(f"  [Event] Current Altitude: {pos.alt_rel:.1f}m", end="\r")
        on_position_update.counter = getattr(on_position_update, "counter", 0) + 1

    drone.on("vehicle_gps_position", on_position_update)

    # ---------------------------------------------------------
    # 3. Data Recording Context
    # ---------------------------------------------------------
    print("\n[3] Starting Background Telemetry Recorder...")
    trace_file = "full_demo_trace.json"
    recorder = Recorder(drone)
    recorder.start()

    # ---------------------------------------------------------
    # 4. Safety Manager Configuration
    # ---------------------------------------------------------
    print("\n[4] Configuring Autonomous Safety Rules...")
    safety = SafetyManager(drone)

    # Example Rule: Land immediately if battery is critically low (ignore 0.0 which often means uninitialized in SITL)
    safety.add_rule(
        SafetyRule(
            condition=lambda s: 0.0 < s.battery_status.remaining_pct < 15,
            action=Land(),
            priority=100,
        )
    )

    # ---------------------------------------------------------
    # 5. Mission Definition & Execution
    # ---------------------------------------------------------
    print("\n[5] Building Mission Sequence...")

    # Autonomous missions require the drone to be in GUIDED mode
    print("Setting vehicle to GUIDED mode...")
    drone.set_mode("GUIDED")

    # Wait for the SITL to stabilize, acquire GPS lock, and confirm mode
    print("Waiting for GPS lock and mode stabilization (5s)...")
    time.sleep(5)

    start_lat = drone.state.vehicle_gps_position.lat
    start_lon = drone.state.vehicle_gps_position.lon

    # Calculate a valid target location (move ~50 meters North/East)
    target_lat = 12.9713390
    target_lon = 80.0438654

    mission = Mission(
        [
            Arm(),
            Takeoff(altitude=10.0, timeout=60),
            Goto(lat=target_lat, lon=target_lon, alt=15.0, timeout=60),
            Land(),
        ]
    )

    print("Executing Mission... (Press Ctrl+C to abort)")
    try:
        # Blocking execution: python will wait here until the mission is completely finished
        drone.execute(mission)
        print("\n\nMission execution completed successfully.")
    except KeyboardInterrupt:
        print("\nMission interrupted by user. Triggering emergency Land...")
        drone.execute(Land())
    finally:
        # ---------------------------------------------------------
        # 6. Cleanup & Trace Playback
        # ---------------------------------------------------------
        print("\n[6] Stopping connection and finalizing trace log...")
        recorder.stop(trace_file)
        drone.close()

        print("\n[7] Initializing Offline Playback (Replay)...")
        if os.path.exists(trace_file):
            print(f"Playing back {trace_file} at 5x speed:")
            player = Player(trace_file)
            player.play(speedup=5.0)
            print("Replay finished!")


if __name__ == "__main__":
    main()
