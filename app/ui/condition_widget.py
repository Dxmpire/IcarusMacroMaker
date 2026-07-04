import customtkinter as ctk

class ConditionWidget(ctk.CTkFrame):
    def __init__(self, master, condition, on_delete=None, on_set_key=None, scale=1.0):
        super().__init__(master, corner_radius=8)

        self.condition = condition
        self.on_delete = on_delete
        self.on_set_key = on_set_key

        # --- SCALE VALUES ---
        font_size = int(16 * scale)
        btn_height = int(32 * scale)
        switch_height = int(28 * scale)
        pad_y = int(5 * scale)
        pad_x = int(10 * scale)

        # --- LABEL ---
        text = self.describe(condition)
        label = ctk.CTkLabel(self, text=text, font=("Arial", font_size))
        label.pack(side="left", padx=pad_x, pady=pad_y)

        t = condition["type"]

        # --- SET KEY BUTTON ---
        if t in ("while_key_down", "toggle_with_key", "action_from_key"):
            key_btn = ctk.CTkButton(
                self,
                text="Set Key",
                width=80,
                height=btn_height,
                command=self.set_key
            )
            key_btn.pack(side="right", padx=pad_x)

        # --- SAFE MODE SWITCH ---
        if t == "action_from_key":
            safe = condition.get("safe_mode", True)
            self.safe_switch = ctk.CTkSwitch(
                self,
                text="Safe Mode",
                height=switch_height,
                command=self.toggle_safe
            )
            if safe:
                self.safe_switch.select()
            else:
                self.safe_switch.deselect()
            self.safe_switch.pack(side="right", padx=pad_x)

        # --- DELETE BUTTON ---
        del_btn = ctk.CTkButton(
            self,
            text="Delete",
            width=80,
            height=btn_height,
            fg_color="#AA0000",
            command=self.delete
        )
        del_btn.pack(side="right", padx=pad_x)

    def describe(self, cond):
        t = cond["type"]
        key = cond.get("key")

        if t == "always_on":
            return "Always On"
        if t == "while_key_down":
            return f"While Key Down ({key or 'unset'})"
        if t == "toggle_with_key":
            return f"Toggle With Key ({key or 'unset'})"
        if t == "while_mouse_down":
            return f"While Mouse Down ({cond.get('button', 'left')})"
        if t == "toggle_with_mouse":
            return f"Toggle With Mouse ({cond.get('button', 'left')})"
        if t == "action_from_key":
            return f"Action From Key ({key or 'unset'})"

        return t

    def set_key(self):
        main = self.winfo_toplevel()
        main.open_change_key_page(self.condition)

    def toggle_safe(self):
        self.condition["safe_mode"] = self.safe_switch.get() == 1

    def delete(self):
        if self.on_delete:
            self.on_delete(self)
