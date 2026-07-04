import customtkinter as ctk

from app.ui.macro_list_page import MacroListPage
from app.ui.macro_editor_page import MacroEditorPage
from app.ui.change_key_page import ChangeKeyPage
from app.ui.settings_page import SettingsPage
from app.ui.profiles_page import ProfilesPage

from app.runtime.runtime_engine import RuntimeEngine
from app.storage.macro_store import MacroStore


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1100x700")
        self.title("Icarus Macro Maker")

        self.store = MacroStore()
        self.engine = RuntimeEngine(store=self.store)

        self._build_sidebar()
        self._build_content()
        self._build_profile_bar()

        self.pages = {
            "macros": MacroListPage(self, on_edit=self.open_editor_page),
            "editor": MacroEditorPage(self, on_back=self.open_macro_list_page),
            "change_key": ChangeKeyPage(self, on_back=self.open_editor_page),
            "settings": SettingsPage(self),
            "profiles": ProfilesPage(self),
        }

        for page in self.pages.values():
            page.place_forget()

        self.show_page("macros")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color="#2B2B2B")
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar,
            text="IMM",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        ctk.CTkButton(
            self.sidebar,
            text="Macros",
            command=self.open_macro_list_page
        ).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            self.sidebar,
            text="Profiles",
            command=self.open_profiles_page
        ).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            self.sidebar,
            text="Settings",
            command=self.open_settings_page
        ).pack(fill="x", padx=10, pady=5)

    def _build_content(self):
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True)

    def _build_profile_bar(self):
        self.active_profile_bar = ctk.CTkFrame(
            self.content,
            fg_color="#1E1E1E",
            height=40
        )
        self.active_profile_bar.pack(fill="x")

        self.active_profile_label = ctk.CTkLabel(
            self.active_profile_bar,
            text=f"Active Profile: {self.engine.active_profile.name}",
            font=("Arial", 16, "bold")
        )
        self.active_profile_label.pack(side="left", padx=20)

    def update_active_profile_label(self):
        self.active_profile_label.configure(
            text=f"Active Profile: {self.engine.active_profile.name}"
        )

    def show_page(self, name):
        for page in self.pages.values():
            page.place_forget()

        self.pages[name].place(in_=self.content, relwidth=1, relheight=1)
        self.update_active_profile_label()

    def open_macro_list_page(self):
        self.show_page("macros")

    def open_editor_page(self, macro=None):
        if macro:
            self.pages["editor"].load_macro(macro)
        self.show_page("editor")

    def open_change_key_page(self, target):
        self.pages["change_key"].load_target(target)
        self.show_page("change_key")

    def open_settings_page(self):
        self.show_page("settings")

    def open_profiles_page(self):
        self.show_page("profiles")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()