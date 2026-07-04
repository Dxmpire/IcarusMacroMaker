import customtkinter as ctk
from app.ui.overlay import Overlay


class RenameMacroOverlay(Overlay):
    def __init__(self, root, macro, on_save=None, on_cancel=None):
        super().__init__(root, on_close=on_cancel)

        self.macro = macro
        self.on_save = on_save

        ctk.CTkLabel(self.panel, text="Rename Macro", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=20)

        self.entry = ctk.CTkEntry(self.panel, width=250)
        self.entry.insert(0, macro.name)
        self.entry.pack(pady=10, padx=20)

        btn_row = ctk.CTkFrame(self.panel, fg_color="transparent")
        btn_row.pack(pady=20, padx=20)

        ctk.CTkButton(btn_row, text="Save", width=100, command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color="#444444", command=self.close).pack(side="right", padx=10)

    def save(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.macro.name = new_name
            if self.on_save:
                self.on_save(self.macro)
        self.destroy()
