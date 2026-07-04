import customtkinter as ctk
from app.ui.overlay import Overlay

ACTION_TYPES = [
    ("Press Key", "key_press"),
    ("Key Down", "key_down"),
    ("Key Up", "key_up"),
    ("Delay", "delay"),
    ("Mouse Click", "mouse_click"),
]


class ActionMenuOverlay(Overlay):
    def __init__(self, root, on_select=None, on_cancel=None):
        super().__init__(root, on_close=on_cancel)

        self.on_select = on_select

        ctk.CTkLabel(self.panel, text="Select Action Type", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=20)

        for label, action_type in ACTION_TYPES:
            ctk.CTkButton(
                self.panel, text=label, width=200,
                command=lambda a=action_type: self.select(a)
            ).pack(pady=5, padx=20)

        ctk.CTkButton(self.panel, text="Cancel", fg_color="#444444", command=self.close).pack(pady=(15, 20), padx=20)

    def select(self, action_type):
        if self.on_select:
            self.on_select(action_type)
        self.destroy()
