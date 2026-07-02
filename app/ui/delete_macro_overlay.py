import customtkinter as ctk

class DeleteMacroOverlay(ctk.CTkFrame):
    def __init__(self, master, macro, on_delete=None, on_cancel=None):
        super().__init__(master, fg_color="#000000")

        self.macro = macro
        self.on_delete = on_delete
        self.on_cancel = on_cancel

        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(panel, text="Delete Macro?", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        msg = ctk.CTkLabel(panel, text="This cannot be undone.", font=("Arial", 16))
        msg.pack(pady=10)

        btn_row = ctk.CTkFrame(panel)
        btn_row.pack(pady=20)

        delete_btn = ctk.CTkButton(btn_row, text="Delete", width=100, fg_color="#AA0000", command=self.delete)
        delete_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(btn_row, text="Cancel", width=100, fg_color="#444444", command=self.cancel)
        cancel_btn.pack(side="right", padx=10)

    def delete(self):
        if self.on_delete:
            self.on_delete(self.macro)
        self.destroy()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()
