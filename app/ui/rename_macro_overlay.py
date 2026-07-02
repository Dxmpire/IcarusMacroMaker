import customtkinter as ctk

class RenameMacroOverlay(ctk.CTkFrame):
    def __init__(self, master, macro, on_save=None, on_cancel=None):
        super().__init__(master, fg_color="#000000")

        self.macro = macro
        self.on_save = on_save
        self.on_cancel = on_cancel

        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(panel, text="Rename Macro", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        self.entry = ctk.CTkEntry(panel, width=250)
        self.entry.insert(0, macro.name)
        self.entry.pack(pady=10)

        btn_row = ctk.CTkFrame(panel)
        btn_row.pack(pady=20)

        save_btn = ctk.CTkButton(btn_row, text="Save", width=100, command=self.save)
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color="#444444", command=self.cancel)
        cancel_btn.pack(side="right", padx=10)

    def save(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.macro.name = new_name
            if self.on_save:
                self.on_save(self.macro)
        self.destroy()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()
