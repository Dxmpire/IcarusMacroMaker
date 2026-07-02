import customtkinter as ctk

class ActionMenuOverlay(ctk.CTkFrame):
    def __init__(self, master, on_select=None, on_cancel=None):
        # Solid dark overlay (no alpha allowed in Tk)
        super().__init__(master, fg_color="#000000")  

        self.on_select = on_select
        self.on_cancel = on_cancel

        # Center panel
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(panel, text="Select Action Type", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        # Action buttons
        actions = [
            ("Press Key", "key_press"),
            ("Key Down", "key_down"),
            ("Key Up", "key_up"),
            ("Delay", "delay"),
            ("Mouse Click", "mouse_click")
        ]

        for label, action_type in actions:
            btn = ctk.CTkButton(panel, text=label, width=200,
                                command=lambda a=action_type: self.select(a))
            btn.pack(pady=5)

        # Cancel button
        cancel_btn = ctk.CTkButton(panel, text="Cancel", fg_color="#444444",
                                   command=self.cancel)
        cancel_btn.pack(pady=20)

    def select(self, action_type):
        if self.on_select:
            self.on_select(action_type)
        self.destroy()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()
