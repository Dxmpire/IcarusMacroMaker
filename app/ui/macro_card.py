import customtkinter as ctk
from app.ui.rename_macro_overlay import RenameMacroOverlay
from app.ui.delete_macro_overlay import DeleteMacroOverlay


class MacroCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        macro,
        on_edit=None,
        on_rename=None,
        on_delete=None,
        on_duplicate=None,
        on_toggle=None
    ):
        # height=1 + pack_propagate(True) lets the card shrink to fit its
        # content instead of sitting at CTkFrame's default height of 200.
        super().__init__(
            master,
            corner_radius=14,
            fg_color="#2A2A2A",
            border_width=1,
            border_color="#3A3A3A",
            height=1
        )
        self.pack_propagate(True)

        self.macro = macro
        self.on_edit = on_edit
        self.on_rename = on_rename
        self.on_delete = on_delete
        self.on_duplicate = on_duplicate
        self.on_toggle = on_toggle

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(fill="x", padx=10, pady=10)

        self._build_header()
        self._build_actions()

    def _build_header(self):
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        self.dot = ctk.CTkFrame(
            left,
            width=8,
            height=8,
            corner_radius=4,
            fg_color="#4CAF50" if self.macro.enabled else "#777777"
        )
        self.dot.pack(side="left", padx=(0, 8))

        self.name = ctk.CTkLabel(left, text=self.macro.name, font=("Arial", 15, "bold"))
        self.name.pack(side="left")

        self.toggle = ctk.CTkSwitch(
            header,
            text="",
            command=self._toggle,
            width=40,
            height=20,
            progress_color="#4CAF50"
        )
        self.toggle.pack(side="right")

        if self.macro.enabled:
            self.toggle.select()
        else:
            self.toggle.deselect()

    def _build_actions(self):
        actions = ctk.CTkFrame(self.main, fg_color="transparent")
        actions.pack(fill="x")

        self._btn(actions, "Edit", self._edit).pack(side="left", padx=(0, 6))
        self._btn(actions, "Rename", self._rename).pack(side="left", padx=6)
        self._btn(actions, "Duplicate", self._duplicate).pack(side="left", padx=6)

        spacer = ctk.CTkFrame(actions, fg_color="transparent")
        spacer.pack(side="left", expand=True)

        self._btn(actions, "Delete", self._delete, danger=True).pack(side="right")

    def _btn(self, parent, text, cmd, danger=False):
        return ctk.CTkButton(
            parent,
            text=text,
            width=90,
            height=28,
            corner_radius=6,
            fg_color="#5A1A1A" if danger else "#3A3A3A",
            hover_color="#7A2222" if danger else "#4A4A4A",
            command=cmd,
            font=("Arial", 12)
        )

    def update_name(self):
        self.name.configure(text=self.macro.name)

    def update_enabled(self):
        self.dot.configure(fg_color="#4CAF50" if self.macro.enabled else "#777777")

        if self.macro.enabled:
            self.toggle.select()
        else:
            self.toggle.deselect()

    def _toggle(self):
        self.macro.enabled = self.toggle.get() == 1
        self.update_enabled()

        if self.on_toggle:
            self.on_toggle(self.macro, self.macro.enabled)

    def _edit(self):
        if self.on_edit:
            self.on_edit(self.macro)

    def _rename(self):
        RenameMacroOverlay(
            self.winfo_toplevel(),
            self.macro,
            on_save=lambda m: (
                self.update_name(),
                self.on_rename and self.on_rename(m)
            )
        ).open()

    def _duplicate(self):
        if self.on_duplicate:
            self.on_duplicate(self.macro)

    def _delete(self):
        DeleteMacroOverlay(
            self.winfo_toplevel(),
            self.macro,
            on_delete=lambda m: self.on_delete and self.on_delete(m)
        ).open()
