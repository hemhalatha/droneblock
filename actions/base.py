from abc import ABC, abstractmethod
from typing import Optional
from ..core.logger import get_logger

log = get_logger("actions.base")

class Action(ABC):
    """Base class for droneblock actions.

    The action lifecycle follows: start -> tick -> complete? -> abort.
    Actions can define an optional timeout to prevent infinite execution.

    Attributes:
        drone: The drone instance this action is bound to.
        timeout (Optional[float]): Maximum execution time in seconds.
        aborted (bool): Whether the action was interrupted.
    """
    def __init__(self, timeout: Optional[float] = None):
        """Initializes the action.

        Args:
            timeout: Maximum execution time in seconds. Must be > 0 if provided.

        Raises:
            ValueError: If timeout is provided and is not positive.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("Action timeout must be a positive float.")
            
        self.drone = None
        self._started = False
        self.aborted = False
        self.timeout = timeout

    def bind(self, drone):
        """Binds the action to a specific drone instance.

        Args:
            drone: The Drone instance to bind to.
        """
        self.drone = drone

    @abstractmethod
    def start(self):
        """Called once when the action begins."""
        pass

    @abstractmethod
    def tick(self):
        """Called periodically (e.g., 10Hz) during execution."""
        pass

    @abstractmethod
    def complete(self) -> bool:
        """Determines if the action has finished.

        Returns:
            True if the action is complete, False otherwise.
        """
        return True

    def abort(self):
        """Called if the action is interrupted by safety or the user."""
        self.aborted = True
        log.warning(f"{self.__class__.__name__} aborted.")

    def __repr__(self):
        return self.__class__.__name__
