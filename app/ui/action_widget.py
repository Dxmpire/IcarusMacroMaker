import customtkinter as ctk

class ActionWidget(ctk.CTkFrame):
    def __init__(
        self,
        master,
        step,
        on_delete=None,
        on_set_key=None,
        on_edit_delay=None,
        on_move=None
    ):
        super().__init__(master, corner_radius=8)

        self.step = step
        self.on_delete = on_delete
        self.on_set_key = on_set_key
        self.on_edit_delay = on_edit_delay
        self.on_move = on_move

        # Store original color for drag restore
        self._original_fg = self.cget("fg_color")

        # -----------------------------
        # MAIN LABEL
        # -----------------------------
        text = self.describe_step(step)
        self.label = ctk.CTkLabel(self, text=text, font=("Arial", 16))
        self.label.pack(side="left", padx=10, pady=5)

        # -----------------------------
        # KEY / DELAY BUTTONS
        # -----------------------------
        t = step.step_type.value

        if t in ("key_press", "key_down", "key_up"):
            ctk.CTkButton(self, text="Set Key", width=80, command=self.set_key).pack(side="right", padx=5)

        if t == "delay":
            ctk.CTkButton(self, text="Edit Delay", width=100, command=self.edit_delay).pack(side="right", padx=5)

        ctk.CTkButton(self, text="Delete", width=80, fg_color="#AA0000",
                      command=self.delete_action).pack(side="right", padx=10)

        # -----------------------------
        # DRAG & DROP
        # -----------------------------
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag_motion)
        self.bind("<ButtonRelease-1>", self._end_drag)

        for child in self.winfo_children():
            child.bind("<Button-1>", self._start_drag)
            child.bind("<B1-Motion>", self._drag_motion)
            child.bind("<ButtonRelease-1>", self._end_drag)

        self._drag_start_y = None
        self._ghost = None
        self._slot = None

    # -----------------------------
    # BUTTON HANDLERS
    # -----------------------------
    def delete_action(self):
        if self.on_delete:
            self.on_delete(self)

    def set_key(self):
        main = self.winfo_toplevel()
        main.open_change_key_page(self.step)

    def edit_delay(self):
        if self.on_edit_delay:
            self.on_edit_delay(self.step)

    # -----------------------------
    # DRAG & DROP WITH FULL GHOST + SLOT
    # -----------------------------
    def _start_drag(self, event):
        self._drag_start_y = event.y_root

        # Dim real widget instead of hiding it
        self.configure(fg_color="#333333")

        # Create full ghost clone
        self._ghost = ctk.CTkFrame(
            self.master,
            fg_color="#555555",
            corner_radius=8,
            width=self.winfo_width(),
            height=self.winfo_height()
        )

        ghost_label = ctk.CTkLabel(
            self._ghost,
            text=self.describe_step(self.step),
            font=("Arial", 16)
        )
        ghost_label.pack(side="left", padx=10, pady=5)

        # Place ghost at widget position
        self._ghost.place(x=self.winfo_x(), y=self.winfo_y())

        # Create drop slot (where the item will land)
        self._slot = ctk.CTkFrame(self.master, fg_color="#888888", height=10)
        self._slot.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())

    def _drag_motion(self, event):
        if not self._ghost:
            return

        # Move ghost with cursor
        new_y = event.y_root - self.master.winfo_rooty()
        self._ghost.place(x=self._ghost.winfo_x(), y=new_y)

        # Move slot to nearest position
        widgets = [
            w for w in self.master.winfo_children()
            if isinstance(w, ActionWidget)
        ]

        for w in widgets:
            wy = w.winfo_y()
            wh = w.winfo_height()

            # If ghost is above midpoint of widget → slot goes above it
            if new_y < wy + wh / 2:
                self._slot.place(x=w.winfo_x(), y=wy)
                break
        else:
            # Place at bottom
            last = widgets[-1]
            self._slot.place(
                x=last.winfo_x(),
                y=last.winfo_y() + last.winfo_height()
            )

    def _end_drag(self, event):
        if not self._ghost:
            return

        dy = event.y_root - self._drag_start_y

        # Cleanup ghost + slot
        self._ghost.destroy()
        self._ghost = None

        self._slot.destroy()
        self._slot = None

        # Restore real widget color
        self.configure(fg_color=self._original_fg)

        # Trigger reorder
        if abs(dy) > 20 and self.on_move:
            direction = -1 if dy < 0 else 1
            self.on_move(self.step, direction)

    # -----------------------------
    # DESCRIPTION
    # -----------------------------
    def describe_step(self, step):
        st = step.step_type
        p = step.params

        if st.value == "key_press":
            return f"Press {p.get('key', '?')}"
        if st.value == "key_down":
            return f"Key Down: {p.get('key', '?')}"
        if st.value == "key_up":
            return f"Key Up: {p.get('key', '?')}"
        if st.value == "delay":
            return f"Wait {p.get('ms', 0)} ms"
        if st.value == "mouse_click":
            return f"Mouse Click ({p.get('button', 'left')})"
        if st.value == "loop":
            return "Loop"

        return st.value
