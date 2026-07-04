import customtkinter as ctk
from app.ui.action_widget import ActionWidget
from app.ui.action_menu_overlay import ActionMenuOverlay
from app.ui.condition_widget import ConditionWidget
from app.ui.condition_menu_overlay import ConditionMenuOverlay
from app.ui.edit_delay_overlay import EditDelayOverlay
from app.models.step import Step, StepType


class MacroEditorPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master)

        self.macro = None
        self.on_back = on_back

        self.scroll = ctk.CTkScrollableFrame(self, width=800, height=600)
        self.scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll, text="Macro Editor", font=("Arial", 28, "bold")).pack(pady=20)

        self._build_category_selector()
        self._build_conditions_section()
        self._build_actions_section()

        ctk.CTkButton(self.scroll, text="Save", command=self._handle_save_and_back).pack(pady=10)

    def _build_category_selector(self):
        ctk.CTkLabel(self.scroll, text="Category", font=("Arial", 20, "bold")).pack(anchor="w", padx=20)

        self.category_dropdown = ctk.CTkOptionMenu(
            self.scroll,
            values=["Uncategorized", "Combat", "Utility", "Movement", "Crafting", "System"],
            command=self._category_changed
        )
        self.category_dropdown.pack(padx=20, pady=10)

    def _build_conditions_section(self):
        ctk.CTkLabel(self.scroll, text="Conditions", font=("Arial", 20, "bold")).pack(anchor="w", padx=20, pady=(10, 0))

        self.conditions_frame = ctk.CTkScrollableFrame(self.scroll, width=600, height=int(160 * 0.65))
        self.conditions_frame.pack(fill="x", padx=20, pady=(5, 5))

        self.add_condition_btn = ctk.CTkButton(self.scroll, text="+ Add Condition", command=self.open_condition_menu)
        self.add_condition_btn.pack(anchor="w", padx=20, pady=(0, 10))

    def _build_actions_section(self):
        ctk.CTkLabel(self.scroll, text="Actions", font=("Arial", 20, "bold")).pack(anchor="w", padx=20, pady=(10, 0))

        self.actions_frame = ctk.CTkScrollableFrame(self.scroll, width=600, height=int(450 * 0.55))
        self.actions_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        self.add_action_btn = ctk.CTkButton(self.scroll, text="+ Add Action", command=self.open_action_menu)
        self.add_action_btn.pack(anchor="w", padx=20, pady=(0, 10))

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

    def _category_changed(self, value):
        self.macro.category = value
        self._save_macro()

    def load_macro(self, macro):
        self.macro = macro
        self.category_dropdown.set(self.macro.category)
        self.refresh_conditions()
        self.refresh_actions()

    # --- Conditions ---

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
            self.winfo_toplevel(),
            on_select=self.condition_type_selected
        ).open()

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
        self.winfo_toplevel().open_change_key_page(condition)

    # --- Actions ---

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
            self.winfo_toplevel(),
            on_select=self.action_type_selected
        ).open()

    def action_type_selected(self, action_type):
        if action_type in ("key_press", "key_down", "key_up"):
            step = Step(StepType[action_type.upper()], {"key": None})
            self.macro.steps.append(step)
            self._save_macro()
            self.winfo_toplevel().open_change_key_page(step)
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
        self.winfo_toplevel().open_change_key_page(step)

    def add_delay_action(self):
        step = Step(StepType.DELAY, {"ms": 100})
        self.macro.steps.append(step)
        self._save_macro()
        self.refresh_actions()

    def edit_delay_action(self, step):
        EditDelayOverlay(
            self.winfo_toplevel(),
            step,
            on_save=self._delay_saved
        ).open()

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

    # --- Reordering ---

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

    def _move_step_drag(self, step, direction):
        steps = self.macro.steps
        idx = steps.index(step)
        new_idx = idx + direction

        if new_idx < 0 or new_idx >= len(steps):
            return

        steps.insert(new_idx, steps.pop(idx))
        self._save_macro()
        self.refresh_actions()
