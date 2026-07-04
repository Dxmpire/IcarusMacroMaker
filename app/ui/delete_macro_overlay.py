import customtkinter as ctk
from app.ui.overlay import Overlay


class DeleteMacroOverlay(Overlay):
    def __init__(self, root, macro, on_delete=None, on_cancel=None):
        super().__init__(root, on_close=on_cancel)

        self.macro = macro
        self.on_delete = on_delete

        ctk.CTkLabel(self.panel, text="Delete Macro?", font=("Arial", 24, "bold")).pack(pady=(20, 10), padx=20)
        ctk.CTkLabel(self.panel, text="This cannot be undone.", font=("Arial", 16)).pack(pady=10, padx=20)

        btn_row = ctk.CTkFrame(self.panel, fg_color="transparent")
        btn_row.pack(pady=20, padx=20)

        ctk.CTkButton(btn_row, text="Delete", width=100, fg_color="#AA0000", command=self.delete).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color="#444444", command=self.close).pack(side="right", padx=10)

    def delete(self):
        if self.on_delete:
            self.on_delete(self.macro)
        self.destroy()
