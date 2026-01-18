from ..core.state import VehicleGpsPosition, VehicleAttitude, BatteryStatus, VehicleStatus

class TelemetryMapper:
    """
    Normalizes raw MAVLink messages (backend events) into uORB topics.
    """
    def __init__(self, events, state):
        self.events = events
        self.state = state
        self._setup_subscriptions()

    def _setup_subscriptions(self):
        """Listen to raw backend messages."""
        self.events.on("mav.GLOBAL_POSITION_INT", self._handle_gps)
        self.events.on("mav.ATTITUDE", self._handle_attitude)
        self.events.on("mav.SYS_STATUS", self._handle_battery)
        self.events.on("mav.HEARTBEAT", self._handle_heartbeat)

    def _handle_gps(self, msg):
        topic = VehicleGpsPosition(
            lat=msg.lat / 1e7,
            lon=msg.lon / 1e7,
            alt_msl=msg.alt / 1000.0,
            alt_rel=msg.relative_alt / 1000.0,
            vel_n_m_s=msg.vx / 100.0,
            vel_e_m_s=msg.vy / 100.0,
            vel_d_m_s=msg.vz / 100.0
        )
        self.state.update_topic("vehicle_gps_position", topic)
        self.events.emit("vehicle_gps_position", topic)

    def _handle_attitude(self, msg):
        topic = VehicleAttitude(
            roll=msg.roll,
            pitch=msg.pitch,
            yaw=msg.yaw
        )
        self.state.update_topic("vehicle_attitude", topic)
        self.events.emit("vehicle_attitude", topic)

    def _handle_battery(self, msg):
        topic = BatteryStatus(
            voltage_v=msg.voltage_battery / 1000.0,
            remaining_pct=msg.battery_remaining
        )
        self.state.update_topic("battery_status", topic)
        self.events.emit("battery_status", topic)
        
        if topic.remaining_pct < 20:
            self.events.emit("safety.battery_low", topic.remaining_pct)

    def _handle_heartbeat(self, msg):
        # Simplified mode mapping
        # Actual mapping depends on autopilot_type which should be set on connection
        armed = bool(msg.base_mode & 128) # MAV_MODE_FLAG_SAFETY_ARMED
        topic = VehicleStatus(
            armed=armed,
            nav_state="N/A" # Ideally resolved by connector mode lookup
        )
        self.state.update_topic("vehicle_status", topic)
        self.events.emit("vehicle_status", topic)
