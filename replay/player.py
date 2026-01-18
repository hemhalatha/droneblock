import json
import time
from ..core.events import EventEmitter
from ..core.state import DroneState
from ..core.logger import get_logger

log = get_logger("replay.player")

class Player:
    """
    Deterministic replay engine for offline trace analysis.
    
    Injects recorded events into a fresh event bus at the correct
    timing intervals. Disables live connectors for pure logic replay.
    """
    def __init__(self, filename: str):
        self.filename = filename
        self.events = EventEmitter()
        self.state = DroneState()
        self.trace = []

    def load(self):
        log.info(f"Loading trace from {self.filename}...")
        with open(self.filename, 'r') as f:
            self.trace = json.load(f)
        log.info(f"Loaded {len(self.trace)} events.")

    def play(self, speedup: float = 1.0):
        if not self.trace:
            self.load()

        log.info(f"Starting replay at {speedup}x speed...")
        start_time = time.monotonic()
        
        for entry in self.trace:
            target_time = entry["time"] / speedup
            while (time.monotonic() - start_time) < target_time:
                time.sleep(0.001)
            
            # Inject event into the bus
            # Note: For dataclass topics, we'd ideally reconstruct the objects
            # For V1, the listeners should be aware they might get dicts if replaying
            log.trace(f"Injecting @ {entry['time']:.2f}s: {entry['event']}")
            self.events.emit(entry["event"], entry["payload"])

        log.info("Replay finished.")
