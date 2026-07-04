import customtkinter as ctk
from app.ui.overlay import Overlay


class EditDelayOverlay(Overlay):
    def __init__(self, root, step, on_save=None, on_cancel=None):
        super().__init__(root, on_close=on_cancel)

        self.step = step
        self.on_save = on_save

        ctk.CTkLabel(self.panel, text="Edit Delay", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=20)

        self.entry = ctk.CTkEntry(self.panel, width=200)
        self.entry.insert(0, str(step.params.get("ms", 100)))
        self.entry.pack(pady=10, padx=20)

        btn_row = ctk.CTkFrame(self.panel, fg_color="transparent")
        btn_row.pack(pady=20, padx=20)

        ctk.CTkButton(btn_row, text="Save", width=100, command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color="#444444", command=self.close).pack(side="right", padx=10)

    def save(self):
        try:
            ms = int(self.entry.get())
        except ValueError:
            ms = 100

        self.step.params["ms"] = max(1, ms)

        if self.on_save:
            self.on_save(self.step)

        self.destroy()
