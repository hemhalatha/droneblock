"""
DroneBlock Exceptions Module.

Defines the custom exceptions used throughout the framework.
"""

class DroneblockError(Exception):
    """Base exception for all droneblock errors."""

class ConnectionError(DroneblockError): # pylint: disable=redefined-builtin
    """Raised when the drone fails to connect or heartbeats are lost."""

class CommandError(DroneblockError):
    """Raised when a MAVLink command is rejected or timed out."""

class SafetyViolation(DroneblockError):
    """Raised when a safety rule is triggered and requires immediate handling."""

class ActionTimeoutError(DroneblockError, TimeoutError):
    """Raised when an action fails to complete within its allotted time."""
