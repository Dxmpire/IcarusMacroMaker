import customtkinter as ctk
from app.ui.rename_profile_overlay import RenameProfileOverlay


class ProfilesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.engine = master.engine
        self.store = self.engine.profile_store

        title = ctk.CTkLabel(self, text="Profiles", font=("Arial", 28, "bold"))
        title.pack(pady=20)

        ctk.CTkButton(self, text="+ Create Profile", command=self.create_profile).pack(pady=10)

        # MAIN SCROLL AREA
        self.scroll = ctk.CTkScrollableFrame(self, width=600, height=600)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        self.refresh()

    # ---------------------------------------------------------
    # REFRESH PAGE
    # ---------------------------------------------------------
    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        active = self.engine.active_profile
        others = [p for p in self.engine.profiles if p != active]

        # ======================================================
        # ACTIVE PROFILE SECTION
        # ======================================================
        active_section = ctk.CTkFrame(self.scroll, fg_color="#2A2A2A")
        active_section.pack(fill="x", pady=10)

        ctk.CTkLabel(
            active_section,
            text="Active Profile",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        row = ctk.CTkFrame(active_section)
        row.pack(fill="x", pady=5)

        ctk.CTkLabel(row, text=active.name, font=("Arial", 20, "bold")).pack(side="left", padx=10)

        ctk.CTkButton(
            row,
            text="Rename",
            width=80,
            command=lambda p=active: self.rename_profile(p)
        ).pack(side="right", padx=5)

        # ======================================================
        # OTHER PROFILES SECTION
        # ======================================================
        if others:
            other_section = ctk.CTkFrame(self.scroll, fg_color="#1F1F1F")
            other_section.pack(fill="x", pady=10)

            ctk.CTkLabel(
                other_section,
                text="Other Profiles",
                font=("Arial", 22, "bold")
            ).pack(anchor="w", padx=10, pady=5)

            for profile in others:
                row = ctk.CTkFrame(other_section)
                row.pack(fill="x", pady=5)

                ctk.CTkLabel(row, text=profile.name, font=("Arial", 20)).pack(side="left", padx=10)

                ctk.CTkButton(
                    row,
                    text="Activate",
                    width=100,
                    command=lambda p=profile: self.activate_profile(p)
                ).pack(side="right", padx=5)

                ctk.CTkButton(
                    row,
                    text="Rename",
                    width=80,
                    command=lambda p=profile: self.rename_profile(p)
                ).pack(side="right", padx=5)

                ctk.CTkButton(
                    row,
                    text="Delete",
                    width=80,
                    fg_color="#AA0000",
                    command=lambda p=profile: self.delete_profile(p)
                ).pack(side="right", padx=5)

    # ---------------------------------------------------------
    # CREATE PROFILE
    # ---------------------------------------------------------
    def create_profile(self):
        name = f"Profile {len(self.engine.get_profiles()) + 1}"
        profile = self.store.create_profile(name)
        self.engine.profiles.append(profile)
        self.refresh()

    # ---------------------------------------------------------
    # ACTIVATE PROFILE
    # ---------------------------------------------------------
    def activate_profile(self, profile):
        self.engine.set_active_profile(profile)
        self.master.pages["macros"].refresh()
        self.master.update_active_profile_label()
        self.refresh()

    # ---------------------------------------------------------
    # DELETE PROFILE
    # ---------------------------------------------------------
    def delete_profile(self, profile):
        if profile == self.engine.active_profile:
            return

        self.store.delete_profile(profile)
        self.engine.profiles.remove(profile)
        self.refresh()

    # ---------------------------------------------------------
    # RENAME PROFILE
    # ---------------------------------------------------------
    def rename_profile(self, profile):
        def on_save(profile, new_name):
            self.store.rename_profile(profile, new_name)
            self.master.update_active_profile_label()
            self.refresh()
            self.master.pages["macros"].refresh()

        RenameProfileOverlay(
            self.winfo_toplevel(),
            profile,
            on_save=on_save
        ).open()