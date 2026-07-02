import customtkinter as ctk
from app.ui.rename_macro_overlay import RenameMacroOverlay
from app.ui.delete_macro_overlay import DeleteMacroOverlay

class MacroCard(ctk.CTkFrame):
    def __init__(self, master, macro, on_edit=None, on_refresh=None, on_duplicate=None):
        super().__init__(master, corner_radius=10)

        self.master = master
        self.macro = macro
        self.on_edit = on_edit
        self.on_refresh = on_refresh
        self.on_duplicate = on_duplicate

        # Macro name
        name_label = ctk.CTkLabel(self, text=macro.name, font=("Arial", 20, "bold"))
        name_label.pack(anchor="w", padx=10, pady=5)

        # ⭐ NEW: Category label
        category_label = ctk.CTkLabel(
            self,
            text=f"[{macro.category}]",
            font=("Arial", 14)
        )
        category_label.pack(anchor="w", padx=10)

        # Status + toggle row
        row = ctk.CTkFrame(self)
        row.pack(fill="x", padx=10, pady=5)

        self.status_label = ctk.CTkLabel(row, text="On" if macro.enabled else "Off", font=("Arial", 14))
        self.status_label.pack(side="left")

        self.toggle = ctk.CTkSwitch(row, text="Enabled", command=self.handle_toggle)

        if macro.enabled:
            self.toggle.select()
        else:
            self.toggle.deselect()

        self.toggle.pack(side="right")

        # Buttons row
        btn_row = ctk.CTkFrame(self)
        btn_row.pack(fill="x", padx=10, pady=10)

        edit_btn = ctk.CTkButton(btn_row, text="Edit", width=80, command=self.handle_edit)
        edit_btn.pack(side="left", padx=5)

        rename_btn = ctk.CTkButton(btn_row, text="Rename", width=80, command=self.handle_rename)
        rename_btn.pack(side="left", padx=5)

        duplicate_btn = ctk.CTkButton(btn_row, text="Duplicate", width=100, command=self.handle_duplicate)
        duplicate_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(btn_row, text="Delete", width=80, fg_color="#AA0000", command=self.handle_delete)
        delete_btn.pack(side="right", padx=5)

    # ---------------------------------------------------------
    # BUTTON HANDLERS
    # ---------------------------------------------------------

    def handle_edit(self):
        if self.on_edit:
            self.on_edit(self.macro)

    def handle_toggle(self):
        root = self.master
        while not hasattr(root, "engine"):
            root = root.master

        is_on = self.toggle.get() == 1
        self.macro.enabled = is_on
        self.status_label.configure(text="On" if is_on else "Off")

        root.engine.set_macro_enabled(self.macro, is_on)
        root.store.save_macro(self.macro)

    def handle_rename(self):
        RenameMacroOverlay(
            self.master.master,
            self.macro,
            on_save=self.rename_done,
            on_cancel=lambda: None
        ).place(relwidth=1, relheight=1)

    def rename_done(self, macro):
        root = self.master
        while not hasattr(root, "store"):
            root = root.master

        root.store.save_macro(macro)

        if self.on_refresh:
            self.on_refresh()

    # ---------------------------------------------------------
    # DUPLICATE HANDLER
    # ---------------------------------------------------------
    def handle_duplicate(self):
        if self.on_duplicate:
            self.on_duplicate(self.macro)

    # ---------------------------------------------------------
    # DELETE HANDLER
    # ---------------------------------------------------------
    def handle_delete(self):
        DeleteMacroOverlay(
            self.master.master,
            self.macro,
            on_delete=self.delete_done,
            on_cancel=lambda: None
        ).place(relwidth=1, relheight=1)

    def delete_done(self, macro):
        root = self.master
        while not hasattr(root, "store"):
            root = root.master

        root.store.delete_macro(macro)
        root.engine.macros.remove(macro)

        if self.on_refresh:
            self.on_refresh()
