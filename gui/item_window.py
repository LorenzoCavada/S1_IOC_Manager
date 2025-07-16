import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import json

from utils.log_handler import logger
from gui.custom_messagebox import YesNoDialogBox, InfoDialogBox, ErrorDialogBox
from data import delete_s1_ioc_by_value

class ItemWindow(ctk.CTkToplevel):
    def __init__(self, parent, value, data):
        super().__init__(parent)
        self.title(f"Item #{value[0]} [{value[4]}]")
        self.geometry(f"500x450")
        
        logger.print_log(f"[INFO] Showing full IOC for element number [{value[0]}].")

        self.title_label = ctk.CTkLabel(self, text=f"Showing the full json for the element number {value[0]}", fg_color="transparent")
        self.title_label.pack(side=tk.TOP, fill="both", padx=5)

        self.json_box = ctk.CTkTextbox(self, state="disabled", text_color="black", font=("Consolas", 10), fg_color="light grey")
        self.json_box.pack(side=tk.TOP, expand=True, fill="both", padx=10, pady=10)

        self.json_box.configure(state="normal") # Temporarily enable
        self.json_box.insert("end", text=f"{data}")
        self.json_box.configure(state="disabled")

        self.get_ioc_button = ctk.CTkButton(self, text="Delete IOC 🗑️", fg_color="red", hover_color="red3", command=lambda: (self._delete_ioc(data)))
        self.get_ioc_button.pack(side=ctk.BOTTOM, pady=10)


    def show(self):
        self.wait_window()

    def _delete_ioc(self, data):
        data = json.loads(data)
        logger.print_log(f"[INFO] User want to delete IOC with value: [{data['value']}]. Asking for confirmation.")

        user_choice = YesNoDialogBox(self, title="Are you sure?", message=f"Do you want to delete the IOC with value: [{data['value']}] from SentinelOne?")
        user_choice = user_choice.show()

        if user_choice:
            logger.print_log(f"[INFO] User want to delete IOC with value: [{data['value']}].")

            result = delete_s1_ioc_by_value(data['value'])

            if result:
                InfoDialogBox(self, title = "IOC deleted", message=f"The IOC [{data['value']}] has been successfully deleted.\nRemember to refresh the table!").show()
                self.destroy()
            else:
                ErrorDialogBox(self, title="IOC deleted", message=f"The IOC [{data['value']}] has NOT been successfully deleted.").show()
        else:
            logger.print_log(f"[INFO] User don't want to delete IOC with value: [{data['value']}]. Moving on.")
        

        

