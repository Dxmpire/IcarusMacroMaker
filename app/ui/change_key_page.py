import customtkinter as ctk

class ChangeKeyPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master)
        self.target = None
        self.on_back = on_back

        title = ctk.CTkLabel(self, text="Press a key...", font=("Arial", 28, "bold"))
        title.pack(pady=20)

    def load_target(self, target):
        self.target = target

        # Bind key capture ONLY when page is shown
        self.master.bind("<Key>", self._capture_key)

    def _capture_key(self, event):
        key = event.keysym

        # Apply key to condition
        if isinstance(self.target, dict):
            self.target["key"] = key
            self.master.pages["editor"].refresh_conditions()

        # Apply key to action
        else:
            self.target.params["key"] = key
            self.master.pages["editor"].refresh_actions()

        # Unbind immediately so other pages don't also capture keystrokes.
        self.master.unbind("<Key>")

        if self.on_back:
            self.on_back()
