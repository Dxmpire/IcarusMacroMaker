import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="Settings", font=("Arial", 28, "bold"))
        title.pack(pady=20)

        ctk.CTkLabel(self, text="(Settings coming soon)").pack(pady=10)
