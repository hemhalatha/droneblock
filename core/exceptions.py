class DroneblockError(Exception):
    """Base exception for all droneblock errors."""
    pass

class ConnectionError(DroneblockError):
    """Raised when the drone fails to connect or heartbeats are lost."""
    pass

class CommandError(DroneblockError):
    """Raised when a MAVLink command is rejected or timed out."""
    pass

class SafetyViolation(DroneblockError):
    """Raised when a safety rule is triggered and requires immediate handling."""
    pass

class ActionTimeoutError(DroneblockError, TimeoutError):
    """Raised when an action fails to complete within its allotted time."""
    pass
