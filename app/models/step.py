from enum import Enum

class StepType(Enum):
    KEY_PRESS = "key_press"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_CLICK = "mouse_click"
    DELAY = "delay"
    LOOP = "loop"

class Step:
    def __init__(self, step_type: StepType, params: dict):
        self.step_type = step_type
        self.params = params

    def to_dict(self):
        return {
            "step_type": self.step_type.value,
            "params": self.params
        }

    @staticmethod
    def from_dict(data: dict):
        return Step(
            step_type=StepType(data["step_type"]),
            params=data["params"]
        )
