"""
DroneBlock Safety Rules Module.

Contains rules and managers for autonomous safety monitoring.
"""

from typing import Callable, List, Any, TYPE_CHECKING
from ..actions.base import Action
from ..core.logger import get_logger

if TYPE_CHECKING:
    from ..core.drone import Drone
    from ..core.state import DroneState

log = get_logger("safety")


class SafetyRule:
    """A context-aware rule that triggers a safety action based on vehicle state.

    Attributes:
        condition (Callable[[DroneState], bool]): Function returning True on violation.
        action (Action): The recovery action to perform (e.g., Land).
        priority (int): Execution priority (higher values are checked first).
        triggered (bool): Internal flag to prevent multiple activations of the same rule.
    """

    def __init__(
        self,
        condition: Callable[["DroneState"], bool],
        action: Action,
        priority: int = 0,
    ) -> None:
        """Initializes a safety rule.

        Args:
            condition: A callable that accepts the drone state and returns a boolean.
            action: The Action object to execute if the condition is met.
            priority: An integer priority level.
        """
        self.condition = condition
        self.action = action
        self.priority = priority
        self.triggered: bool = False


class SafetyManager:
    """Orchestrator for vehicle safety constraints.

    Continuously monitors telemetry events and evaluates registered SafetyRules
    against the current vehicle state. High-priority violations will
    immediately interrupt the current mission or action.

    Attributes:
        drone (Drone): The drone instance to monitor.
        rules (List[SafetyRule]): Sorted list of safety constraints.
    """

    def __init__(self, drone: "Drone") -> None:
        """Initializes the SafetyManager.

        Args:
            drone: The Drone instance.
        """
        self.drone = drone
        self.rules: List[SafetyRule] = []
        self._setup_monitoring()

    def add_rule(self, rule: SafetyRule) -> None:
        """Adds a new safety constraint to the engine.

        Args:
            rule: A SafetyRule object.
        """
        self.rules.append(rule)
        rule.action.bind(self.drone)
        # Sort rules so highest priority are checked first
        self.rules.sort(key=lambda x: x.priority, reverse=True)

    def _setup_monitoring(self) -> None:
        """Registers internal event handlers for telemetry monitoring."""
        # Generic check triggered on major telemetry updates
        self.drone.on("vehicle_gps_position", self._check_rules)
        self.drone.on("battery_status", self._check_rules)

    def _check_rules(self, _data: Any = None) -> None:
        """Internal callback to evaluate all rules against the current state.

        Args:
            data: Data payload from the event emitter (not directly used).
        """
        state = self.drone.state
        for rule in self.rules:
            if not rule.triggered and rule.condition(state):
                log.warning(
                    "SAFETY VIOLATION DETECTED (Priority %d): %s",
                    rule.priority,
                    rule.action,
                )
                rule.triggered = True

                # Interrupt the currently executing mission step
                if self.drone.current_action:
                    log.info(
                        "Aborting current action '%s' due to safety constraint.",
                        self.drone.current_action,
                    )
                    self.drone.current_action.abort()

                # Immediately initiate the safety recovery action
                log.info("Starting safety action: %s", rule.action)
                rule.action.start()

                # Only the highest priority violation is handled in a single evaluation tick
                break
