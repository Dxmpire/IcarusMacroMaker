import customtkinter as ctk

class MenuPage(ctk.CTkFrame):
    def __init__(self, master, on_open_macros, on_open_settings, on_open_profiles):
        super().__init__(master)

        title = ctk.CTkLabel(self, text="Icarus Macro Maker", font=("Arial", 32, "bold"))
        title.pack(pady=40)

        ctk.CTkButton(self, text="Macros", width=200, command=on_open_macros).pack(pady=10)
        ctk.CTkButton(self, text="Profiles", width=200, command=on_open_profiles).pack(pady=10)
        ctk.CTkButton(self, text="Settings", width=200, command=on_open_settings).pack(pady=10)
