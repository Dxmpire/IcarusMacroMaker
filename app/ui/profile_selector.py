import customtkinter as ctk

class ProfileSelector(ctk.CTkFrame):
    def __init__(self, master, engine, on_change=None):
        super().__init__(master)

        self.engine = engine
        self.on_change = on_change

        ctk.CTkLabel(self, text="Profile", font=("Arial", 16, "bold")).pack(anchor="w")

        # Dropdown
        self.dropdown = ctk.CTkOptionMenu(
            self,
            values=[p.name for p in engine.get_profiles()],
            command=self._profile_selected
        )
        self.dropdown.pack(fill="x", pady=5)

        # Set initial
        self.dropdown.set(engine.active_profile.name)

    def refresh(self):
        self.dropdown.configure(values=[p.name for p in self.engine.get_profiles()])
        self.dropdown.set(self.engine.active_profile.name)

    def _profile_selected(self, name):
        for p in self.engine.get_profiles():
            if p.name == name:
                self.engine.set_active_profile(p)
                break

        if self.on_change:
            self.on_change()
