import time
from typing import List, Union
from ..actions.base import Action
from ..core.logger import get_logger
from ..core.exceptions import DroneblockError, ActionTimeoutError

log = get_logger("mission")

class Mission:
    """A collection of actions to be executed sequentially.

    Attributes:
        actions (List[Action]): The sequence of actions to run.
    """
    def __init__(self, actions: List[Action]):
        """Initializes the mission.

        Args:
            actions: List of Action objects.
        """
        self.actions = actions

class MissionExecutor:
    """Sequential runner for droneblock missions.

    Manages the lifecycle of actions, enforces timeouts, and emits events
    via the drone's shared event bus.

    Attributes:
        drone: The drone instance to execute missions on.
    """
    def __init__(self, drone):
        """Initializes the executor.

        Args:
            drone: The Drone instance.
        """
        self.drone = drone

    def run(self, mission_or_action: Union[Mission, Action], blocking: bool = True):
        """Executes an Action or a Mission.

        Args:
            mission_or_action: The sequence or atomic behavior to run.
            blocking: If True, waits for completion. If False, runs in a daemon thread.

        Returns:
            The execution thread if non-blocking, otherwise None.
        """
        if blocking:
            self._execute(mission_or_action)
        else:
            import threading
            thread = threading.Thread(target=self._execute, args=(mission_or_action,), daemon=True)
            thread.start()
            return thread

    def _execute(self, mission_or_action):
        """Internal execution loop.

        Args:
            mission_or_action: The mission or action to execute.

        Raises:
            ActionTimeoutError: If an action exceeds its defined timeout.
            DroneblockError: If an action fails due to an unexpected error.
        """
        actions = mission_or_action.actions if isinstance(mission_or_action, Mission) else [mission_or_action]
        
        log.info(f"Starting {len(actions)} actions...")
        for action in actions:
            action.bind(self.drone)
            self.drone.current_action = action
            log.info(f"Executing {action}")
            
            # Emit ActionStarted event
            self.drone.events.emit("action.started", action)
            
            start_time = time.time()
            action.start()
            
            try:
                while not action.complete():
                    if action.aborted:
                        log.warning(f"Action {action} was aborted. Terminating sequence.")
                        return
                    
                    # Timeout enforcement
                    if action.timeout:
                        elapsed = time.time() - start_time
                        if elapsed > action.timeout:
                            log.error(f"Action {action} timed out after {elapsed:.2f}s")
                            self.drone.events.emit("action.timeout", action)
                            action.abort()
                            raise ActionTimeoutError(f"Action {action} timed out after {action.timeout}s")
                    
                    action.tick()
                    time.sleep(0.1)
            except ActionTimeoutError:
                raise
            except Exception as e:
                log.error(f"Execution error during {action}: {e}")
                raise DroneblockError(f"Action {action} failed: {e}")
            
            log.info(f"Action {action} finished.")
        
        self.drone.current_action = None
        log.info("Mission Complete.")
