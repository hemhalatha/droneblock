"""
Advanced droneblock Demonstration
--------------------------------------
This script demonstrates a full end-to-end workflow:
1. Establishing a MAVLink connection to SITL.
2. Setting up the asynchronous trace recorder.
3. Defining priority-based safety constraints.
4. Implementing custom telemetry logic via the event bus.
5. Executing a multi-stage sequential mission.
"""

import time
from droneblock import Drone, Arm, Takeoff, Goto, Land, Mission
# Note: Replay and Safety modules remain in their submodules but can be imported cleanly
from droneblock.safety.rules import SafetyRule, SafetyManager
from droneblock.replay.recorder import Recorder

def main():
    # STEP 1: Initialization
    # We connect to PX4 SITL using the default UDP port 14540.
    # The Drone class automatically initializes the uORB state store 
    # and the telemetry mapper.
    print("--- droneblock Demo ---")
    try:
        drone = Drone.connect("udp://:14540")
    except Exception as e:
        print(f"Error: {e}")
        print("Tip: Run PX4 SITL (e.g., 'make px4_sitl jmavsim') first.")
        return

    # STEP 2: Data Observability & Recording
    # The Recorder creates a high-res trace of all telemetry topics and action triggers.
    # This JSON trace can later be used with the Replay Player for logic validation.
    recorder = Recorder(drone)
    recorder.start()

    # STEP 3: Safety Configuration
    # SafetyRules are context-aware and priority-driven. 
    # If the battery falls below 20%, the 'Land' action will immediately 
    # interrupt the current mission step.
    safety = SafetyManager(drone)
    safety.add_rule(SafetyRule(
        condition=lambda s: s.battery_status.remaining_pct < 20,
        action=Land(),
        priority=10
    ))

    # STEP 4: Telemetry Interaction (uORB Pub/Sub style)
    # You can register lambda or function handlers for any uORB topic.
    # Here we print altitude using the 'vehicle_gps_position' topic.
    drone.on("vehicle_gps_position", lambda pos: print(f"Alt: {pos.alt_rel:.2f}m", end='\r'))

    # STEP 5: Mission Definition
    # Missions are lists of reusable Action objects.
    # droneblock handles the sequential transition between steps.
    mission = Mission([
        Arm(),
        Takeoff(5),
        Goto(drone.state.vehicle_gps_position.lat + 0.0001, 
             drone.state.vehicle_gps_position.lon + 0.0001, 5),
        Land()
    ])

    # STEP 6: Execution
    # We run the mission in blocking mode for this demo.
    # Non-blocking execution is possible via 'blocking=False'.
    try:
        drone.execute(mission)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        # STEP 7: Cleanup & Persistence
        # Save the recorder trace to disk before exiting.
        recorder.stop("sitl_mission_trace.json")
        print("Demo finished.")

if __name__ == "__main__":
    main()
