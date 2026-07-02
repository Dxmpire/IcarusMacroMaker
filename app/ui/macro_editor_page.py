import customtkinter as ctk
from app.ui.action_widget import ActionWidget
from app.ui.action_menu_overlay import ActionMenuOverlay
from app.ui.condition_widget import ConditionWidget
from app.ui.condition_menu_overlay import ConditionMenuOverlay
from app.models.step import Step, StepType


class MacroEditorPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master)

        self.macro = None
        self.on_back = on_back

        title = ctk.CTkLabel(self, text="Macro Editor", font=("Arial", 28, "bold"))
        title.pack(pady=20)

        # ============================================================
        # CATEGORY SELECTOR
        # ============================================================
        cat_label = ctk.CTkLabel(self, text="Category", font=("Arial", 20, "bold"))
        cat_label.pack(anchor="w", padx=20)

        self.category_dropdown = ctk.CTkOptionMenu(
            self,
            values=[
                "Uncategorized",
                "Combat",
                "Utility",
                "Movement",
                "Crafting",
                "System"
            ],
            command=self._category_changed
        )
        self.category_dropdown.pack(padx=20, pady=10)

        # ============================================================
        # CONDITIONS (small + scrollable)
        # ============================================================
        cond_label = ctk.CTkLabel(self, text="Conditions", font=("Arial", 20, "bold"))
        cond_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.conditions_frame = ctk.CTkScrollableFrame(
            self,
            width=600,
            height=160   # ⭐ SMALL FIXED HEIGHT
        )
        self.conditions_frame.pack(fill="x", padx=20, pady=(5, 5))

        self.add_condition_btn = ctk.CTkButton(
            self,
            text="+ Add Condition",
            command=self.open_condition_menu
        )
        self.add_condition_btn.pack(anchor="w", padx=20, pady=(0, 10))

        # ============================================================
        # ACTIONS (large main editor)
        # ============================================================
        act_label = ctk.CTkLabel(self, text="Actions", font=("Arial", 20, "bold"))
        act_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.actions_frame = ctk.CTkScrollableFrame(
            self,
            width=600,
            height=450   # ⭐ LARGE AREA
        )
        self.actions_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.add_action_btn = ctk.CTkButton(
            self,
            text="+ Add Action",
            command=self.open_action_menu
        )
        self.add_action_btn.pack(anchor="w", padx=20, pady=(0, 10))

        # Save button
        save_btn = ctk.CTkButton(self, text="Save", command=self._handle_save_and_back)
        save_btn.pack(pady=10)

    # ============================================================
    # INTERNAL: SAVE MACRO
    # ============================================================
    def _save_macro(self):
        if not self.macro:
            return

        root = self.winfo_toplevel()
        if hasattr(root, "store"):
            root.store.save_macro(self.macro)

    def _handle_save_and_back(self):
        self._save_macro()
        if self.on_back:
            self.on_back()

    # ============================================================
    # CATEGORY HANDLER
    # ============================================================
    def _category_changed(self, value):
        self.macro.category = value
        self._save_macro()

    # ============================================================
    # LOAD MACRO
    # ============================================================
    def load_macro(self, macro):
        self.macro = macro
        self.category_dropdown.set(self.macro.category)
        self.refresh_conditions()
        self.refresh_actions()

    # ============================================================
    # CONDITIONS
    # ============================================================
    def refresh_conditions(self):
        for w in self.conditions_frame.winfo_children():
            w.destroy()

        for cond in self.macro.conditions:
            ConditionWidget(
                self.conditions_frame,
                cond,
                on_delete=self.delete_condition,
                on_set_key=self.set_condition_key
            ).pack(fill="x", pady=5)

    def open_condition_menu(self):
        ConditionMenuOverlay(
            self,
            on_select=self.condition_type_selected,
            on_cancel=lambda: None
        ).place(relwidth=1, relheight=1)

    def condition_type_selected(self, cond_type):
        cond = {"type": cond_type}

        if cond_type in ("while_key_down", "toggle_with_key", "action_from_key"):
            cond["key"] = None

        if cond_type == "action_from_key":
            cond["safe_mode"] = True

        self.macro.conditions.append(cond)
        self._save_macro()
        self.refresh_conditions()

    def delete_condition(self, widget):
        cond = widget.condition
        if cond in self.macro.conditions:
            self.macro.conditions.remove(cond)
        self._save_macro()
        self.refresh_conditions()

    def set_condition_key(self, condition):
        main = self.winfo_toplevel()
        main.open_change_key_page(condition)

    # ============================================================
    # ACTIONS
    # ============================================================
    def refresh_actions(self):
        for w in self.actions_frame.winfo_children():
            w.destroy()

        for step in self.macro.steps:
            ActionWidget(
                self.actions_frame,
                step,
                on_delete=self.delete_action,
                on_set_key=self.set_action_key,
                on_edit_delay=self.edit_delay_action,
                on_move=self._move_step_drag
            ).pack(fill="x", pady=5)

    def open_action_menu(self):
        ActionMenuOverlay(
            self,
            on_select=self.action_type_selected,
            on_cancel=lambda: None
        ).place(relwidth=1, relheight=1)

    def action_type_selected(self, action_type):
        if action_type in ("key_press", "key_down", "key_up"):
            step = Step(StepType[action_type.upper()], {"key": None})
            self.macro.steps.append(step)
            self._save_macro()

            main = self.winfo_toplevel()
            main.open_change_key_page(step)
            return

        if action_type == "delay":
            self.add_delay_action()
            return

        if action_type == "mouse_click":
            self.add_mouse_click_action()
            return

        if action_type == "loop":
            self.add_loop_action()
            return

    def set_action_key(self, step):
        main = self.winfo_toplevel()
        main.open_change_key_page(step)

    def add_delay_action(self):
        step = Step(StepType.DELAY, {"ms": 100})
        self.macro.steps.append(step)
        self._save_macro()
        self.refresh_actions()

    def edit_delay_action(self, step):
        from app.ui.edit_delay_overlay import EditDelayOverlay
        EditDelayOverlay(
            self.winfo_toplevel(),
            step,
            on_save=self._delay_saved,
            on_cancel=lambda: None
        ).place(relwidth=1, relheight=1)

    def _delay_saved(self, step):
        self._save_macro()
        self.refresh_actions()

    def add_mouse_click_action(self):
        step = Step(StepType.MOUSE_CLICK, {"button": "left"})
        self.macro.steps.append(step)
        self._save_macro()
        self.refresh_actions()

    def add_loop_action(self):
        step = Step(StepType.LOOP, {})
        self.macro.steps.append(step)
        self._save_macro()
        self.refresh_actions()

    def delete_action(self, widget):
        step = widget.step
        if step in self.macro.steps:
            self.macro.steps.remove(step)
        self._save_macro()
        self.refresh_actions()

    # ============================================================
    # MOVE ACTIONS
    # ============================================================
    def move_action_up(self, widget):
        step = widget.step
        idx = self.macro.steps.index(step)
        if idx > 0:
            self.macro.steps[idx], self.macro.steps[idx - 1] = \
                self.macro.steps[idx - 1], self.macro.steps[idx]
        self._save_macro()
        self.refresh_actions()

    def move_action_down(self, widget):
        step = widget.step
        idx = self.macro.steps.index(step)
        if idx < len(self.macro.steps) - 1:
            self.macro.steps[idx], self.macro.steps[idx + 1] = \
                self.macro.steps[idx + 1], self.macro.steps[idx]
        self._save_macro()
        self.refresh_actions()

    # ============================================================
    # DRAG & DROP REORDERING
    # ============================================================
    def _move_step_drag(self, step, direction):
        steps = self.macro.steps
        idx = steps.index(step)
        new_idx = idx + direction

        if new_idx < 0 or new_idx >= len(steps):
            return

        steps.insert(new_idx, steps.pop(idx))
        self._save_macro()
        self.refresh_actions()
