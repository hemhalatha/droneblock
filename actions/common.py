from .base import Action
import pymavlink.mavutil as mavutil
from ..core.logger import get_logger

log = get_logger("actions")

class Arm(Action):
    def start(self):
        log.info("Arming...")
        self.drone.arm()

    def tick(self):
        pass

    def complete(self):
        return self.drone.state.vehicle_status.armed

class Takeoff(Action):
    def __init__(self, altitude: float):
        super().__init__()
        self.altitude = altitude

    def start(self):
        log.info(f"Taking off to {self.altitude}m...")
        self.drone.connector.send_command(
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            p7=self.altitude
        )

    def tick(self):
        pass

    def complete(self):
        current_alt = self.drone.state.vehicle_gps_position.alt_rel
        return abs(current_alt - self.altitude) < 0.5

class Goto(Action):
    def __init__(self, lat: float, lon: float, alt: float):
        super().__init__()
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def start(self):
        log.info(f"Going to {self.lat}, {self.lon}, {self.alt}...")
        self.drone.connector.send_command(
            mavutil.mavlink.MAV_CMD_DO_REPOSITION,
            p7=self.alt,
            p5=self.lat,
            p6=self.lon
        )

    def tick(self):
        pass

    def complete(self):
        gps = self.drone.state.vehicle_gps_position
        dist = ((gps.lat - self.lat)**2 + (gps.lon - self.lon)**2)**0.5
        return dist < 1e-5 and abs(gps.alt_rel - self.alt) < 0.5

class Land(Action):
    def start(self):
        log.info("Landing...")
        self.drone.set_mode("LAND")

    def tick(self):
        pass

    def complete(self):
        status = self.drone.state.vehicle_status
        gps = self.drone.state.vehicle_gps_position
        return not status.armed or gps.alt_rel < 0.2
