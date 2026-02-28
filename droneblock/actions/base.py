"""
DroneBlock Base Action Module.

Provides abstract foundation for all flight behaviors.
"""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from ..core.logger import get_logger

if TYPE_CHECKING:
    from ..core.drone import Drone

log = get_logger("actions.base")

class Action(ABC):
    """Abstract base class for all DroneBlock actions.

    The action lifecycle is managed by a MissionExecutor and consists of:
    1. start(): Initialization logic.
    2. tick(): Periodic execution logic.
    3. complete(): Termination check.
    4. abort(): Cleanup if interrupted.

    Attributes:
        drone (Optional[Drone]): The drone instance this action is bound to.
        timeout (Optional[float]): Maximum allowed execution time in seconds.
        aborted (bool): Flag indicating if the action was cancelled.
    """

    def __init__(self, timeout: Optional[float] = None) -> None:
        """Initializes the action.

        Args:
            timeout: Maximum execution time in seconds. Must be > 0.

        Raises:
            ValueError: If timeout is non-positive.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("Action timeout must be a positive float.")

        self.drone: Optional['Drone'] = None
        self._started: bool = False
        self.aborted: bool = False
        self.timeout: Optional[float] = timeout

    def bind(self, drone: 'Drone') -> None:
        """Associates the action with a drone instance.

        Args:
            drone: The Drone instance to control.
        """
        self.drone = drone

    @abstractmethod
    def start(self) -> None:
        """Logic to execute when the action starts."""

    @abstractmethod
    def tick(self) -> None:
        """Logic to execute periodically during the action's lifecycle."""

    @abstractmethod
    def complete(self) -> bool:
        """Condition that determines if the action has finished successfully.

        Returns:
            True if target reached or condition met, False otherwise.
        """
        return True

    def abort(self) -> None:
        """Interrupts the action and performs any necessary cleanup."""
        self.aborted = True
        log.warning("Action '%s' aborted.", self.__class__.__name__)

    def __repr__(self) -> str:
        return self.__class__.__name__
