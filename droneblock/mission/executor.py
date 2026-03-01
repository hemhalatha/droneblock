"""
DroneBlock Mission Executor Module.

Handles the sequential execution and lifecycle of drone missions.
"""

import time
import threading
from typing import List, Union, Optional, TYPE_CHECKING
from ..actions.base import Action
from ..core.logger import get_logger
from ..core.exceptions import DroneblockError, ActionTimeoutError

if TYPE_CHECKING:
    from ..core.drone import Drone

log = get_logger("mission")


class Mission:
    """A formal sequence of Actions to be executed by the vehicle.

    Attributes:
        actions (List[Action]): The ordered list of actions to perform.
    """

    def __init__(self, actions: List[Action]) -> None:
        """Initializes a Mission instance.

        Args:
            actions: A list of Action objects.
        """
        self.actions = actions


class MissionExecutor:
    """Orchestrator for sequential action execution on a Drone.

    Handles the lifecycle transitions of actions, enforces time constraints,
    and publishes progress updates to the drone's event bus.

    Attributes:
        drone (Drone): The drone instance to execute on.
    """

    def __init__(self, drone: "Drone") -> None:
        """Initializes the executor.

        Args:
            drone: The Drone instance.
        """
        self.drone = drone

    def run(
        self, mission_or_action: Union[Mission, Action], blocking: bool = True
    ) -> Optional[threading.Thread]:
        """Initiates execution of a mission or a single action.

        Args:
            mission_or_action: The target to execute.
            blocking: If True, the call waits for completion.
                      If False, it returns immediately after starting a thread.

        Returns:
            The background thread if non-blocking, otherwise None.
        """
        if blocking:
            self._execute(mission_or_action)
            return None

        thread = threading.Thread(
            target=self._execute,
            args=(mission_or_action,),
            daemon=True,
            name="MissionExecutorThread",
        )
        thread.start()
        return thread

    def _execute(self, mission_or_action: Union[Mission, Action]) -> None:
        """Internal execution loop managing the action lifecycle.

        Args:
            mission_or_action: The mission or action to execute.

        Raises:
            ActionTimeoutError: If an action exceeds its time limit.
            DroneblockError: For any unexpected failures during execution.
        """
        actions = (
            mission_or_action.actions
            if isinstance(mission_or_action, Mission)
            else [mission_or_action]
        )

        log.info("Executing sequence with %d actions.", len(actions))
        for action in actions:
            action.bind(self.drone)
            self.drone.current_action = action

            log.info("Starting action: %s", action)
            self.drone.events.emit("action.started", action)

            start_time = time.time()
            action.start()

            try:
                self._wait_for_action(action, start_time)
            except ActionTimeoutError:
                raise
            except Exception as e:
                log.error(
                    "Critical error during execution of '%s': %s",
                    action,
                    e,
                    exc_info=True,
                )
                raise DroneblockError(f"Action '{action}' failed due to: {e}") from e

            log.info("Action '%s' completed successfully.", action)

        self.drone.current_action = None
        log.info("Mission execution sequence finished.")

    def _wait_for_action(self, action: Action, start_time: float) -> None:
        """Blocks and monitors the execution of a single action until completion or failure.

        Args:
            action: The active action being monitored.
            start_time: The timestamp when the action was started.

        Raises:
            ActionTimeoutError: If the action exceeds its designated timeout duration.
        """
        while not action.complete():
            if action.aborted:
                log.warning("Action '%s' was aborted. Stopping waiting.", action)
                break

            # Enforce timeout if specified
            if action.timeout:
                elapsed = time.time() - start_time
                if elapsed > action.timeout:
                    log.error("Action '%s' timed out after %.2fs", action, elapsed)
                    self.drone.events.emit("action.timeout", action)
                    action.abort()
                    raise ActionTimeoutError(
                        f"Action '{action}' exceeded timeout of {action.timeout}s"
                    )

            action.tick()
            time.sleep(0.1)  # 10Hz control loop
