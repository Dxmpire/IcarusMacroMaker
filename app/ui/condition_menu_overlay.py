import customtkinter as ctk
from app.ui.overlay import Overlay

CONDITION_TYPES = [
    ("always_on", "Always On"),
    ("while_key_down", "While Key Down"),
    ("toggle_with_key", "Toggle With Key"),
    ("while_mouse_down", "While Mouse Down"),
    ("toggle_with_mouse", "Toggle With Mouse"),
    ("action_from_key", "Action From Key"),
]


class ConditionMenuOverlay(Overlay):
    def __init__(self, root, on_select=None, on_cancel=None):
        super().__init__(root, on_close=on_cancel)

        self.on_select = on_select

        ctk.CTkLabel(self.panel, text="Add Condition", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=20)

        for cond_type, label in CONDITION_TYPES:
            ctk.CTkButton(
                self.panel, text=label, width=200,
                command=lambda t=cond_type: self.select(t)
            ).pack(pady=5, padx=20)

        ctk.CTkButton(self.panel, text="Cancel", fg_color="#444444", command=self.close).pack(pady=(10, 20), padx=20)

    def select(self, cond_type):
        if self.on_select:
            self.on_select(cond_type)
        self.destroy()
