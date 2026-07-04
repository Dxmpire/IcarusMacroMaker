import customtkinter as ctk


class Overlay(ctk.CTkFrame):
    """
    Standard full-window modal overlay.

    Always attaches to the real app root instead of whichever frame
    happened to trigger it, so every overlay is the same size and
    always centers correctly, regardless of where it's opened from.

    Subclasses build their content into `self.panel` and should call
    `self.close()` (not `self.destroy()`) when the user cancels, so
    the on_close callback still fires.
    """

    def __init__(self, root, panel_width=320, on_close=None):
        super().__init__(root, fg_color="#000000")
        self.root = root
        self.on_close = on_close

        self.panel = ctk.CTkFrame(self, corner_radius=12, width=panel_width)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

    def open(self):
        self.place(in_=self.root, relwidth=1, relheight=1)
        self.lift()
        return self

    def close(self):
        if self.on_close:
            self.on_close()
        self.destroy()
