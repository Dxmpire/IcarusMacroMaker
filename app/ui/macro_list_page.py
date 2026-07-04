import customtkinter as ctk
from app.ui.macro_card import MacroCard
from app.models.macro import Macro
import copy


class MacroListPage(ctk.CTkFrame):
    def __init__(self, master, on_edit=None):
        super().__init__(master)

        self.master = master
        self.on_edit = on_edit

        # HEADER
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=20)

        title = ctk.CTkLabel(header, text="Macros", font=("Arial", 28, "bold"))
        title.pack(side="left")

        create_btn = ctk.CTkButton(
            header,
            text="＋ Create Macro",
            width=140,
            height=36,
            command=self.create_macro
        )
        create_btn.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.card_widgets = {}

        self._init_cards()

    def _init_cards(self):
        active = self.master.engine.active_profile

        for macro in active.macros:
            self._create_card_for_macro(macro)

        self._rebuild_list()

    def refresh(self):
        # Called when the active profile changes (or is renamed) so the
        # macro list rebuilds from scratch for the new profile's macros.
        for card in self.card_widgets.values():
            card.destroy()

        self.card_widgets = {}
        self._init_cards()

    def _create_card_for_macro(self, macro):
        card = MacroCard(
            self.scroll_frame,
            macro,
            on_edit=self.on_edit,
            on_rename=self._on_macro_renamed,
            on_delete=self._on_macro_deleted,
            on_duplicate=self._on_macro_duplicated
        )

        self.card_widgets[macro] = card

    def _rebuild_list(self):
        # Re-pack existing card widgets in the current macro order
        # without destroying and recreating them.
        for card in self.card_widgets.values():
            card.pack_forget()

        active = self.master.engine.active_profile

        for macro in active.macros:
            card = self.card_widgets.get(macro)
            if not card:
                continue

            card.pack(
                fill="x",
                padx=5,
                pady=5,
                anchor="n"
            )

    def create_macro(self):
        macro = Macro("New Macro")
        macro.enabled = False
        macro.steps = []
        macro.conditions = []

        active = self.master.engine.active_profile
        active.macros.append(macro)

        filename = f"{macro.name}.json"
        if filename not in active.macro_files:
            active.macro_files.append(filename)

        self.master.store.save_macro(macro)
        self.master.engine.profile_store.save_profile(active)

        self.master.engine.macros = active.macros

        self._create_card_for_macro(macro)
        self._rebuild_list()

    def _on_macro_duplicated(self, macro):
        new_macro = copy.deepcopy(macro)
        new_macro.name = f"{macro.name} (copy)"

        active = self.master.engine.active_profile
        active.macros.append(new_macro)

        filename = f"{new_macro.name}.json"
        if filename not in active.macro_files:
            active.macro_files.append(filename)

        self.master.store.save_macro(new_macro)
        self.master.engine.profile_store.save_profile(active)

        self.master.engine.macros = active.macros

        self._create_card_for_macro(new_macro)
        self._rebuild_list()

    def _on_macro_deleted(self, macro):
        active = self.master.engine.active_profile

        if macro in active.macros:
            active.macros.remove(macro)

        filename = f"{macro.name}.json"
        if filename in active.macro_files:
            active.macro_files.remove(filename)

        self.master.store.delete_macro(macro)
        self.master.engine.profile_store.save_profile(active)

        self.master.engine.macros = active.macros

        card = self.card_widgets.pop(macro, None)
        if card:
            card.destroy()

        self._rebuild_list()

    def _on_macro_renamed(self, macro):
        self._rebuild_list()