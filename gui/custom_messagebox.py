import tkinter as tk
import customtkinter as ctk

class YesNoDialogBox(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)

        self.geometry(f"{len(message)*7 + 20}x{100}")
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

class UpdateIOCDialogBox(ctk.CTkToplevel):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.title("IOC Already uploaded on S1")

        self.geometry(f"500x450")
        self.resizable(False, False)

        self.wait_visibility()
        self.grab_set()  # Make it modal

        # Message
        self.label = ctk.CTkLabel(self, text="The IOC is already available on S1 with the following value. Do you want to update it?", justify="center")
        self.label.pack(side=tk.TOP, fill="both", padx=5)

        self.json_box = ctk.CTkTextbox(self, state="disabled", text_color="black", font=("Consolas", 10), fg_color="light grey")
        self.json_box.pack(side=tk.TOP, expand=True, fill="both", padx=10, pady=10)

        self.json_box.configure(state="normal") # Temporarily enable
        self.json_box.insert("end", text=f"{data}")
        self.json_box.configure(state="disabled")

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0,20))

        self.choice = None
        yes_btn = ctk.CTkButton(btn_frame, text="Update", width=80, command=self._on_yes)
        yes_btn.pack(side="left", padx=10)
        no_btn = ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self._on_no)
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

class InfoDialogBox(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)

        self.geometry(f"{len(message)*7 + 20}x{100}")
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
        yes_btn = ctk.CTkButton(btn_frame, text="Ok!", width=80, command=self._exit)
        yes_btn.pack(side="bottom", padx=10)

        self.protocol("WM_DELETE_WINDOW", self._exit)

    def _exit(self):
        self.destroy()

    def show(self):
        self.wait_window()
        return None

class ErrorDialogBox(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(f"⚠️ {title} ⚠️")

        self.geometry(f"{len(message)*7 + 20}x{100}")
        self.resizable(False, False)

        self.wait_visibility()
        self.grab_set()  # Make it modal

        # Message
        self.label = ctk.CTkLabel(self, text=f"{message}", justify="center")
        self.label.pack(pady=(20,10), padx=10, expand=True)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0,20))

        self.choice = None
        yes_btn = ctk.CTkButton(btn_frame, text="Ok!", width=80, command=self._exit)
        yes_btn.pack(side="bottom", padx=10)

        self.protocol("WM_DELETE_WINDOW", self._exit)

    def _exit(self):
        self.destroy()

    def show(self):
        self.wait_window()
        return None