import tkinter as tk
import customtkinter as ctk

class YesNoDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)

        self.geometry(f"{len(message)*6 + 20}x{100}")
        self.resizable(False, False)

        self.wait_visibility()
        self.grab_set()  # Make it modal

        # Message
        self.label = ctk.CTkLabel(self, text=message, justify="center")
        self.label.pack(pady=(20,10), padx=10, expand=True)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0,20))

        self.choice = None
        yes_btn = ctk.CTkButton(btn_frame, text="Yes", width=80, command=self._on_yes)
        yes_btn.pack(side="left", padx=10)
        no_btn = ctk.CTkButton(btn_frame, text="No", width=80, command=self._on_no)
        no_btn.pack(side="right", padx=10)

        self.protocol("WM_DELETE_WINDOW", self._on_no)  # Treat window-close as No

    def _on_yes(self):
        self.choice = True
        self.destroy()

    def _on_no(self):
        self.choice = False
        self.destroy()

    def show(self):
        self.wait_window()
        return self.choice