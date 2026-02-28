"""
DroneBlock Replay Player Module.

Engine for deterministic playback of recorded flight traces.
"""
import json
import time
from typing import List, Dict, Any
from ..core.events import EventEmitter
from ..core.state import DroneState
from ..core.logger import get_logger

log = get_logger("replay.player")

class Player:
    """Deterministic replay engine for offline telemetry analysis.

    Injects recorded events into a simulated vehicle environment (state and bus)
    at the original timing intervals. This is used to verify flight logic, 
    safety rules, and mission execution without live hardware.

    Attributes:
        filename (str): Path to the recorded JSON trace file.
        events (EventEmitter): Simulated event bus for replay.
        state (DroneState): Simulated vehicle state synchronized with replayed data.
        trace (List[Dict[str, Any]]): Loaded event data.
    """

    def __init__(self, filename: str) -> None:
        """Initializes the player.

        Args:
            filename: Path to a valid DroneBlock trace file.
        """
        self.filename = filename
        self.events = EventEmitter()
        self.state = DroneState()
        self.trace: List[Dict[str, Any]] = []

    def load(self) -> None:
        """Loads and parses the trace file from disk.

        Raises:
            FileNotFoundError: If the trace file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        log.info("Loading flight trace: '%s'", self.filename)
        with open(self.filename, 'r', encoding='utf-8') as f:
            self.trace = json.load(f)
        log.info("Successfully loaded %d entries.", len(self.trace))

    def play(self, speedup: float = 1.0) -> None:
        """Executes the replay session.

        Args:
            speedup: Factor by which to accelerate playback (e.g., 2.0 for double speed).
        """
        if not self.trace:
            self.load()

        log.info("Starting deterministic replay at %sx speed.", speedup)
        start_real_time = time.monotonic()

        for entry in self.trace:
            # Calculate when this event should fire in 'accelerated' time
            target_replay_time = entry["time"] / speedup

            # Precise wait loop
            while (time.monotonic() - start_real_time) < target_replay_time:
                time.sleep(0.001)

            # Emit the event exactly as it was recorded
            # Note: Consumers of these events must handle dictionary payloads
            # if they expect dataclasses, as JSON serialization is lossy regarding types.
            log.trace("Injecting event '%s' at T+%.3fs", entry['event'], entry['time'])
            self.events.emit(entry["event"], entry["payload"])

        log.info("Replay sequence completed successfully.")
