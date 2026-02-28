"""
DroneBlock State Module.

Defines the data structures representing the vehicle's state.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class VehicleGpsPosition:
    """Represents the vehicle's GPS position and velocity."""
    lat: float = 0.0
    lon: float = 0.0
    alt_msl: float = 0.0
    alt_rel: float = 0.0
    vel_n_m_s: float = 0.0
    vel_e_m_s: float = 0.0
    vel_d_m_s: float = 0.0

@dataclass
class VehicleAttitude:
    """Represents the vehicle's orientation."""
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

@dataclass
class BatteryStatus:
    """Represents the vehicle's battery conditions."""
    voltage_v: float = 0.0
    remaining_pct: float = 0.0

@dataclass
class VehicleStatus:
    """Represents the general operational status of the vehicle."""
    armed: bool = False
    nav_state: str = "UNKNOWN"
    autopilot_type: str = "UNKNOWN"

class DroneState:
    """
    Centralized store for drone state, organized by uORB-style topics.
    """
    def __init__(self):
        self.vehicle_gps_position = VehicleGpsPosition()
        self.vehicle_attitude = VehicleAttitude()
        self.battery_status = BatteryStatus()
        self.vehicle_status = VehicleStatus()

    def update_topic(self, topic_name: str, data: Any):
        """Update a specific topic in the state."""
        if hasattr(self, topic_name):
            setattr(self, topic_name, data)

    def to_dict(self) -> Dict[str, Any]:
        """Snapshots the entire state for recording/replay."""
        return {
            "vehicle_gps_position": asdict(self.vehicle_gps_position),
            "vehicle_attitude": asdict(self.vehicle_attitude),
            "battery_status": asdict(self.battery_status),
            "vehicle_status": asdict(self.vehicle_status)
        }

    def __str__(self) -> str:
        return (
            f"State(Armed={self.vehicle_status.armed}, "
            f"Mode={self.vehicle_status.nav_state}, "
            f"Alt={self.vehicle_gps_position.alt_rel:.1f}m)"
        )
