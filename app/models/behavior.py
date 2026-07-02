from enum import Enum

class BehaviorMode(Enum):
    TOGGLE = "toggle"
    WHILE_HELD = "while_held"
    RUN_ONCE = "run_once"
    LOOP_WHILE_TOGGLED = "loop_while_toggled"

class Behavior:
    def __init__(self,
                 mode: BehaviorMode = BehaviorMode.TOGGLE,
                 activation_delay: int = 0,
                 cooldown: int = 0,
                 cancel_key: str | None = None):
        self.mode = mode
        self.activation_delay = activation_delay
        self.cooldown = cooldown
        self.cancel_key = cancel_key

    def to_dict(self):
        return {
            "mode": self.mode.value,
            "activation_delay": self.activation_delay,
            "cooldown": self.cooldown,
            "cancel_key": self.cancel_key
        }

    @staticmethod
    def from_dict(data: dict):
        return Behavior(
            mode=BehaviorMode(data["mode"]),
            activation_delay=data.get("activation_delay", 0),
            cooldown=data.get("cooldown", 0),
            cancel_key=data.get("cancel_key")
        )
