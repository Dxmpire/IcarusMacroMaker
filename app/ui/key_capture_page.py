import customtkinter as ctk

class KeyCapturePage(ctk.CTkFrame):
    def __init__(self, master, on_cancel=None):
        super().__init__(master)

        self.on_cancel = on_cancel

        label = ctk.CTkLabel(self, text="Press any key...", font=("Arial", 28))
        label.pack(pady=40)

        cancel_btn = ctk.CTkButton(self, text="Cancel", fg_color="#444444", command=self.cancel)
        cancel_btn.pack(pady=20)

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
