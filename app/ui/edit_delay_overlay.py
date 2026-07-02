import customtkinter as ctk

class EditDelayOverlay(ctk.CTkFrame):
    def __init__(self, master, step, on_save=None, on_cancel=None):
        super().__init__(master, fg_color="#000000")

        self.step = step
        self.on_save = on_save
        self.on_cancel = on_cancel

        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(panel, text="Edit Delay", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        self.entry = ctk.CTkEntry(panel, width=200)
        self.entry.insert(0, str(step.params.get("ms", 100)))
        self.entry.pack(pady=10)

        btn_row = ctk.CTkFrame(panel)
        btn_row.pack(pady=20)

        save_btn = ctk.CTkButton(btn_row, text="Save", width=100, command=self.save)
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color="#444444", command=self.cancel)
        cancel_btn.pack(side="right", padx=10)

    def save(self):
        try:
            ms = int(self.entry.get())
            self.step.params["ms"] = max(1, ms)
        except:
            self.step.params["ms"] = 100

        if self.on_save:
            self.on_save(self.step)

        self.destroy()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()
