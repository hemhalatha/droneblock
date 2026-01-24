import json
import time
from typing import Any, List, Dict, TYPE_CHECKING
from dataclasses import asdict, is_dataclass
from ..core.logger import get_logger

if TYPE_CHECKING:
    from ..core.drone import Drone

log = get_logger("replay.recorder")

class Recorder:
    """Telemetry and event recording engine for post-flight analysis.

    Subscribes to designated telemetry topics on the vehicle's event bus 
    and snapshots the data with high-resolution monotonic timestamps. 
    The resulting trace can be used for debugging or deterministic replay.

    Attributes:
        drone (Drone): The drone instance to record.
        trace (List[Dict[str, Any]]): In-memory buffer of recorded events.
        is_recording (bool): Active recording status flag.
    """

    def __init__(self, drone: 'Drone') -> None:
        """Initializes the recorder for a specific drone.

        Args:
            drone: The Drone instance to observe.
        """
        self.drone = drone
        self.trace: List[Dict[str, Any]] = []
        self._start_time: float = 0.0
        self.is_recording: bool = False

    def start(self, topics: Optional[List[str]] = None) -> None:
        """Begins the recording session.

        Args:
            topics: Optional list of event topics to record. If None,
                   a default set of critical telemetry topics is used.
        """
        log.info("Initiating flight trace recording.")
        self.is_recording = True
        self._start_time = time.monotonic()
        
        default_topics = [
            "vehicle_gps_position", 
            "vehicle_attitude", 
            "battery_status", 
            "vehicle_status",
            "action.started",
            "action.timeout"
        ]
        active_topics = topics or default_topics

        for topic in active_topics:
            # We use a default argument t=topic to capture the loop variable correctly
            self.drone.on(topic, lambda data, t=topic: self._record_event(t, data))
        
        log.info(f"Recorder active for topics: {', '.join(active_topics)}")

    def _record_event(self, name: str, data: Any) -> None:
        """Snapshots a single event and appends it to the trace.

        Args:
            name: The topic name of the event.
            data: The event payload (expected to be a dataclass or primitive).
        """
        if not self.is_recording:
            return
            
        timestamp = time.monotonic() - self._start_time
        
        # Serialize dataclasses to dictionaries for JSON compatibility
        if is_dataclass(data):
            payload = asdict(data)
        else:
            payload = data

        self.trace.append({
            "time": timestamp,
            "event": name,
            "payload": payload
        })

    def stop(self, filename: str = "flight_trace.json") -> None:
        """Stops the recording session and persists the trace to disk.

        Args:
            filename: The target JSON file path.
        """
        self.is_recording = False
        log.info(f"Recording stopped. Persisting {len(self.trace)} entries to '{filename}'.")
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.trace, f, indent=2)
            log.info("Trace file saved successfully.")
        except Exception as e:
            log.error(f"Failed to save trace file: {e}")
