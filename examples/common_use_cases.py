"""
Common Use-Cases for droneblock
-----------------------------------
This file contains modular snippets for common drone control patterns.
"""

from droneblock.core.drone import Drone
from droneblock.actions.common import Arm, Takeoff, Goto, Land
from droneblock.mission.executor import Mission
from droneblock.safety.rules import SafetyRule, SafetyManager
from droneblock.replay.recorder import Recorder
from droneblock.replay.player import Player

def simple_mission_example():
    """
    USE-CASE 1: Simple Sequential Mission
    Connects, arms, takes off, moves, and lands.
    """
    print("--- Use-Case: Simple Mission ---")
    drone = Drone.connect("udp://:14540")
    
    # Define a sequence of actions
    mission = Mission([
        Arm(),
        Takeoff(altitude=5.0),
        Goto(lat=47.3977, lon=8.5456, alt=5.0),
        Land()
    ])
    
    # Execute (blocking)
    drone.execute(mission)

def safety_override_example():
    """
    USE-CASE 2: Safety Override (Battery Failsafe)
    Demonstrates how a safety rule interrupts a running mission.
    """
    print("--- Use-Case: Safety Override ---")
    drone = Drone.connect("udp://:14540")
    
    # Setup Safety Manager
    safety = SafetyManager(drone)
    
    # Add a high-priority rule (Priority 10)
    safety.add_rule(SafetyRule(
        condition=lambda state: state.battery_status.remaining_pct < 20,
        action=Land(),
        priority=10
    ))
    
    # Start a long mission
    long_mission = Mission([
        Arm(),
        Takeoff(10),
        Goto(47.4, 8.5, 10), # Far away
        Land()
    ])
    
    # If battery drops during 'Goto', 'Land' will trigger immediately.
    drone.execute(long_mission)

def replay_usage_example():
    """
    USE-CASE 3: Recording and Replaying
    How to persistence flight traces and verify them offline.
    """
    print("--- Use-Case: Replay ---")
    
    # 1. RECORDING
    drone = Drone.connect("udp://:14540")
    recorder = Recorder(drone)
    recorder.start()
    
    # Perform some actions
    drone.execute(Mission([Arm(), Takeoff(2), Land()]))
    
    recorder.stop("flight_trace.json")
    
    # 2. REPLAYING (can be in a separate script)
    print("Starting Offline Replay...")
    player = Player("flight_trace.json")
    player.play(speedup=2.0)

if __name__ == "__main__":
    # Uncomment the usage you want to test
    # simple_mission_example()
    # safety_override_example()
    # replay_usage_example()
    pass
