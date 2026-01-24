"""
DroneBlock: A professional, event-driven drone control framework.

This package provides a high-level API for vehicle control, mission execution,
and real-time telemetry processing across multiple backend connectors.
"""

from .core.drone import Drone
from .core.events import EventEmitter
from .core.state import DroneState
from .actions.base import Action
from .mission.executor import Mission, MissionExecutor

__version__ = "1.0.0"
__all__ = [
    "Drone",
    "EventEmitter",
    "DroneState",
    "Action",
    "Mission",
    "MissionExecutor",
]
