import customtkinter as ctk
from app.ui.overlay import Overlay


class RenameProfileOverlay(Overlay):
    def __init__(self, root, profile, on_save=None, on_cancel=None):
        super().__init__(root, on_close=on_cancel)

        self.profile = profile
        self.on_save = on_save

        ctk.CTkLabel(self.panel, text="Rename Profile", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=20)

        self.entry = ctk.CTkEntry(self.panel, width=250)
        self.entry.insert(0, profile.name)
        self.entry.pack(pady=10, padx=20)

        btn_row = ctk.CTkFrame(self.panel, fg_color="transparent")
        btn_row.pack(pady=20, padx=20)

        ctk.CTkButton(btn_row, text="Save", width=100, command=self.save).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color="#444444", command=self.close).pack(side="right", padx=10)

    def save(self):
        new_name = self.entry.get().strip()
        if new_name and self.on_save:
            self.on_save(self.profile, new_name)
        self.destroy()