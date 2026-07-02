import customtkinter as ctk
from app.ui.macro_card import MacroCard
from app.models.macro import Macro
import copy

class MacroListPage(ctk.CTkFrame):
    def __init__(self, master, on_edit=None):
        super().__init__(master)

        self.master = master
        self.on_edit = on_edit

        title = ctk.CTkLabel(self, text="Macros", font=("Arial", 28, "bold"))
        title.pack(pady=20)

        add_btn = ctk.CTkButton(self, text="+ Create Macro", command=self.create_macro)
        add_btn.pack(pady=10)

        # ⭐ SCROLLABLE FRAME FOR MACRO CARDS
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=600, height=500)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.refresh()

    def refresh(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        # ⭐ Always read macros from the active profile
        active = self.master.engine.active_profile

        for macro in active.macros:
            MacroCard(
                self.scroll_frame,
                macro,
                on_edit=self.on_edit,
                on_refresh=self.refresh,
                on_duplicate=self.duplicate_macro
            ).pack(fill="x", pady=10)

    # ---------------------------------------------------------
    # CREATE MACRO (FIXED)
    # ---------------------------------------------------------
    def create_macro(self):
        macro = Macro("New Macro")
        macro.enabled = False
        macro.category = "Uncategorized"
        macro.steps = []
        macro.conditions = []

        active = self.master.engine.active_profile

        # Add macro to profile
        active.macros.append(macro)

        # Add filename to profile
        filename = f"{macro.name}.json"
        if filename not in active.macro_files:
            active.macro_files.append(filename)

        # Save macro + profile
        self.master.store.save_macro(macro)
        self.master.engine.profile_store.save_profile(active)

        # Sync runtime engine
        self.master.engine.macros = active.macros
        self.master.engine._reset_runtime_state()

        self.refresh()

    # ---------------------------------------------------------
    # MACRO DUPLICATION (FIXED)
    # ---------------------------------------------------------
    def duplicate_macro(self, macro):
        new_macro = copy.deepcopy(macro)
        new_macro.name = f"{macro.name} (copy)"

        active = self.master.engine.active_profile

        # Add to profile
        active.macros.append(new_macro)

        filename = f"{new_macro.name}.json"
        if filename not in active.macro_files:
            active.macro_files.append(filename)

        # Save macro + profile
        self.master.store.save_macro(new_macro)
        self.master.engine.profile_store.save_profile(active)

        # Sync runtime engine
        self.master.engine.macros = active.macros
        self.master.engine._reset_runtime_state()

        self.refresh()
