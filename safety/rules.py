from typing import Callable, List, Any
from ..actions.base import Action
from ..core.logger import get_logger

log = get_logger("safety")

class SafetyRule:
    """
    A context-aware rule that triggers an action based on a state condition.
    
    Attributes:
        condition: A callable that returns True when safety is violated.
        action: The Action to execute if triggered.
        priority: Higher integer values are evaluated first.
    """
    def __init__(self, condition: Callable[[Any], bool], action: Action, priority: int = 0):
        self.condition = condition
        self.action = action
        self.priority = priority
        self.triggered = False

class SafetyManager:
    """
    Priority-based safety rule engine.
    Rules are evaluated continuously; first high-priority trigger wins the tick.
    """
    def __init__(self, drone):
        self.drone = drone
        self.rules: List[SafetyRule] = []
        self._setup_monitoring()

    def add_rule(self, rule: SafetyRule):
        self.rules.append(rule)
        rule.action.bind(self.drone)
        # Sort by priority descending
        self.rules.sort(key=lambda x: x.priority, reverse=True)

    def _setup_monitoring(self):
        # We can monitor any uORB topic or raw event
        self.drone.on("vehicle_gps_position", self._check_rules)
        self.drone.on("battery_status", self._check_rules)
        self.drone.on("safety.battery_low", lambda pct: self._check_rules(None)) # Manual trigger check

    def _check_rules(self, _):
        # Higher priority rules are checked first
        for rule in self.rules:
            if not rule.triggered and rule.condition(self.drone.state):
                log.warning(f"!!! Priority {rule.priority} Interrupt: {rule.action} !!!")
                rule.triggered = True
                
                # Interrupt current action
                if self.drone.current_action:
                    self.drone.current_action.abort()
                
                # Execute safety action
                rule.action.start()
                
                # In each tick, only one safety action (the highest priority) should trigger
                break 
