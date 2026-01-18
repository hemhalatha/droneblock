import threading
import time
from pymavlink import mavutil
from ..core.connector import BaseConnector
from ..core.logger import get_logger

log = get_logger("connectors.pymavlink")

class PymavlinkConnector(BaseConnector):
    """
    Pymavlink implementation of the Droneblock connector.
    Adapts synchronous pymavlink to the async event model.
    """
    def __init__(self, connection_url: str, events):
        super().__init__(connection_url, events)
        self.mav = None
        self._running = False
        self._thread = None
        self.target_system = 1
        self.target_component = 1

    def connect(self):
        log.info(f"Connecting to {self.url}...")
        self.mav = mavutil.mavlink_connection(self.url)
        
        # Wait for heartbeat to identify system IDs
        msg = self.mav.wait_heartbeat(timeout=10)
        if not msg:
            raise ConnectionError("Timeout waiting for heartbeat")
            
        self.target_system = self.mav.target_system
        self.target_component = self.mav.target_component
        
        self._running = True
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()
        log.info(f"Connected (Sys: {self.target_system}, Comp: {self.target_component})")

    def _recv_loop(self):
        while self._running:
            try:
                msg = self.mav.recv_msg()
                if msg:
                    # Emit raw message event
                    self.events.emit(f"mav.{msg.get_type()}", msg)
            except Exception as e:
                log.error(f"Recv error: {e}")
            time.sleep(0.001) # High frequency for telemetry

    def send_command(self, command, p1=0, p2=0, p3=0, p4=0, p5=0, p6=0, p7=0):
        self.mav.mav.command_long_send(
            self.target_system,
            self.target_component,
            command,
            0, # confirmation
            p1, p2, p3, p4, p5, p6, p7
        )

    def arm(self):
        self.send_command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1)

    def disarm(self):
        self.send_command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0)

    def set_mode(self, mode_name: str):
        if mode_name not in self.mav.mode_mapping():
            log.warning(f"Unknown mode: {mode_name}")
            return
        mode_id = self.mav.mode_mapping()[mode_name]
        self.mav.set_mode(mode_id)

    def close(self):
        self._running = False
        if self.mav:
            self.mav.close()
