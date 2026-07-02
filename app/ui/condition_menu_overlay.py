import customtkinter as ctk

class ConditionMenuOverlay(ctk.CTkFrame):
    def __init__(self, master, on_select=None, on_cancel=None):
        super().__init__(master, fg_color="#000000")

        self.on_select = on_select
        self.on_cancel = on_cancel

        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(panel, text="Add Condition", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        self.options = [
            ("always_on", "Always On"),
            ("while_key_down", "While Key Down"),
            ("toggle_with_key", "Toggle With Key"),
            ("while_mouse_down", "While Mouse Down"),
            ("toggle_with_mouse", "Toggle With Mouse"),
            ("action_from_key", "Action From Key")  # NEW CONDITION
        ]

        for t, label in self.options:
            btn = ctk.CTkButton(panel, text=label, width=200,
                                command=lambda tt=t: self.select(tt))
            btn.pack(pady=5)

        cancel_btn = ctk.CTkButton(panel, text="Cancel", fg_color="#444444",
                                   command=self.cancel)
        cancel_btn.pack(pady=10)

    def select(self, cond_type):
        if self.on_select:
            self.on_select(cond_type)
        self.destroy()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()
