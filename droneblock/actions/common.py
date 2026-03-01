"""
DroneBlock Common Actions Module.

Provides standard flight behavior actions like Arm, Takeoff, Goto, and Land.
"""

from pymavlink import mavutil
from .base import Action
from ..core.logger import get_logger

log = get_logger("actions")


class Arm(Action):
    """Arms the drone's motors."""

    def start(self):
        log.info("Arming...")
        self.drone.arm()

    def tick(self):
        pass

    def complete(self):
        return self.drone.state.vehicle_status.armed


class Takeoff(Action):
    """Initiates a vertical takeoff to a specified relative altitude."""

    def __init__(self, altitude: float, **kwargs):
        super().__init__(**kwargs)
        self.altitude = altitude

    def start(self):
        log.info("Taking off to %sm...", self.altitude)
        # Use MAV_CMD_NAV_TAKEOFF with purely positional altitude
        self.drone.connector.send_command(
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            p5=0,  # Latitude (0 = current)
            p6=0,  # Longitude (0 = current)
            p7=self.altitude,
        )

    def tick(self):
        pass

    def complete(self):
        current_alt = self.drone.state.vehicle_gps_position.alt_rel
        return current_alt >= (self.altitude - 0.5)


class Goto(Action):
    """Commands the drone to fly to a specific GPS coordinate and altitude."""

    def __init__(self, lat: float, lon: float, alt: float, **kwargs):
        super().__init__(**kwargs)
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def start(self):
        log.info("Going to %s, %s, %s...", self.lat, self.lon, self.alt)
        # Delegate positional targeting to the backend connector
        self.drone.connector.goto(self.lat, self.lon, self.alt)

    def tick(self):
        pass

    def complete(self):
        gps = self.drone.state.vehicle_gps_position
        dist = ((gps.lat - self.lat) ** 2 + (gps.lon - self.lon) ** 2) ** 0.5
        # Relax the completion radius slightly to ~2.7 meters
        return dist < 2.5e-5 and abs(gps.alt_rel - self.alt) < 0.5


class Land(Action):
    """Commands the drone to land at its current position."""

    def start(self):
        log.info("Landing...")
        self.drone.set_mode("LAND")

    def tick(self):
        pass

    def complete(self):
        status = self.drone.state.vehicle_status
        gps = self.drone.state.vehicle_gps_position
        return not status.armed or gps.alt_rel < 0.2
