import os
import json

MACRO_DIR = os.path.join("app", "storage", "macros")


class MacroStore:
    def __init__(self):
        os.makedirs(MACRO_DIR, exist_ok=True)

    # ---------------------------------------------------------
    # LOAD ONE MACRO (used by RuntimeEngine for profiles)
    # ---------------------------------------------------------
    def load_single_macro(self, path):
        from app.models.macro import Macro
        from app.models.step import Step, StepType

        with open(path, "r") as f:
            data = json.load(f)

        # Build Macro object manually (no from_dict in your class)
        macro = Macro(data["name"])
        macro.enabled = data.get("enabled", False)
        macro.category = data.get("category", "Uncategorized")

        # Steps
        macro.steps = []
        for s in data.get("steps", []):
            step = Step(StepType(s["type"]), s["params"])
            macro.steps.append(step)

        # Conditions
        macro.conditions = data.get("conditions", [])

        return macro

    # ---------------------------------------------------------
    # SAVE MACRO
    # ---------------------------------------------------------
    def save_macro(self, macro):
        data = {
            "name": macro.name,
            "enabled": macro.enabled,
            "category": macro.category,
            "steps": [
                {"type": step.step_type.value, "params": step.params}
                for step in macro.steps
            ],
            "conditions": macro.conditions
        }

        path = os.path.join(MACRO_DIR, f"{macro.name}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # ---------------------------------------------------------
    # DELETE MACRO
    # ---------------------------------------------------------
    def delete_macro(self, macro):
        path = os.path.join(MACRO_DIR, f"{macro.name}.json")
        if os.path.exists(path):
            os.remove(path)

    # ---------------------------------------------------------
    # RENAME MACRO
    # ---------------------------------------------------------
    def rename_macro(self, old_name, new_name):
        old_path = os.path.join(MACRO_DIR, f"{old_name}.json")
        new_path = os.path.join(MACRO_DIR, f"{new_name}.json")
        if os.path.exists(old_path):
            os.rename(old_path, new_path)

    # ---------------------------------------------------------
    # LOAD ALL MACROS (used at startup)
    # ---------------------------------------------------------
    def load_all(self, MacroClass, StepClass, StepType):
        macros = []

        for filename in os.listdir(MACRO_DIR):
            if not filename.endswith(".json"):
                continue

            path = os.path.join(MACRO_DIR, filename)
            with open(path, "r") as f:
                data = json.load(f)

            macro = MacroClass(data["name"])
            macro.enabled = data.get("enabled", False)
            macro.category = data.get("category", "Uncategorized")

            # Steps
            macro.steps = []
            for s in data.get("steps", []):
                step = StepClass(StepType(s["type"]), s["params"])
                macro.steps.append(step)

            # Conditions
            macro.conditions = data.get("conditions", [])

            macros.append(macro)

        return macros
