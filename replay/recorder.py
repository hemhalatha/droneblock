import json
import time
from typing import Any
from ..core.logger import get_logger

log = get_logger("replay.recorder")

class Recorder:
    """
    Observer-based trace recorder for logic validation.
    
    Subscribes to all uORB topics and state changes, serializing 
    them with high-resolution monotonic timestamps.
    """
    def __init__(self, drone):
        self.drone = drone
        self.trace = []
        self._start_time = time.monotonic()
        self._is_recording = False

    def start(self):
        log.info("Trace recording started.")
        self._is_recording = True
        self._start_time = time.monotonic()
        
        # Subscribe to EVERYTHING on the bus
        # This requires small modification to EventEmitter to support '*' (wildcard)
        # For V1 simplicity, we'll manually list the topics we want to record
        topics = [
            "vehicle_gps_position", 
            "vehicle_attitude", 
            "battery_status", 
            "vehicle_status",
            "safety.battery_low"
        ]
        for topic in topics:
            self.drone.on(topic, lambda data, t=topic: self._record_event(t, data))

    def _record_event(self, name: str, data: Any):
        if not self._is_recording:
            return
            
        timestamp = time.monotonic() - self._start_time
        
        # Snapshot the data (if it's a dataclass, convert to dict)
        if hasattr(data, '__dict__'):
            # Simple way to handle dataclasses
            from dataclasses import asdict
            try:
                payload = asdict(data)
            except:
                payload = str(data)
        else:
            payload = data

        self.trace.append({
            "time": timestamp,
            "event": name,
            "payload": payload
        })

    def stop(self, filename: str = "drone_trace.json"):
        self._is_recording = False
        log.info(f"Trace recording stopped. Saving {len(self.trace)} events to {filename}...")
        with open(filename, 'w') as f:
            json.dump(self.trace, f, indent=2)
