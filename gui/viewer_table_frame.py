import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from dateutil import parser
from datetime import datetime
import json

from utils.log_handler import logger

from gui.custom_messagebox import YesNoDialogBox, InfoDialogBox, ErrorDialogBox

from data import get_s1_ioc_by_value, delete_s1_ioc_by_value

colums_settings = {
    'num': {'allignment': tk.CENTER, 'size': 40},
    'name': {'allignment': tk.W},
    'description': {'allignment': tk.W},
    'type': {'allignment': tk.CENTER, 'size': 50},
    'value': {'allignment': tk.CENTER},
    'metadata': {'allignment': tk.CENTER},          
    'source': {'allignment': tk.CENTER, 'size': 140},                
    'creationTime': {'allignment': tk.CENTER, 'size': 160},
    'updatedAt': {'allignment': tk.CENTER, 'size': 160},
    'validUntil': {'allignment': tk.CENTER, 'size': 160}
}

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

class ViewerTableFrame(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.tree = None
        self.build_table(data)

        # Let this frame expand with its parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def build_table(self, data):
        logger.print_log("[INFO] Building the IOC table.")
        self.tree = ttk.Treeview(self, columns=list(data[0].keys()), show="headings")
        
        for col in data[0].keys():
            heading = col
            alignment = colums_settings[col].get("allignment", tk.CENTER)
            width = colums_settings[col].get("size", None)

            stretch = width is None

            self.tree.heading(col, text=heading)
            self.tree.column(col, anchor=alignment, stretch=stretch, width=width if width else 100)

        for row in data:
            row['creationTime'] = parser.parse(row['creationTime']).strftime("%d/%m/%Y %H:%M:%S") if row.get('creationTime') else ""
            row['updatedAt']    = parser.parse(row['updatedAt']).strftime("%d/%m/%Y %H:%M:%S")    if row.get('updatedAt') else ""
            row['validUntil']   = parser.parse(row['validUntil']).strftime("%d/%m/%Y %H:%M:%S")   if row.get('validUntil') else ""
            self.tree.insert("", "end", values=list(row.values()))

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self.row_double_click)

    def row_double_click(self, event):        
        item_id = self.tree.identify_row(event.y)  # Get the item ID under mouse
        if item_id:
            value = self.tree.item(item_id, "values")
            logger.print_log(f"[INFO] Double click on item [{value[0]}] detected. Showing detailed pop up window.")

            ioc_data = get_s1_ioc_by_value(value[4])            

            if(ioc_data != None):
                ioc_data = json.dumps(ioc_data, indent=2)
                item_window = ItemWindow(self, value=value, data=ioc_data)
                item_window.show()
            else:
                logger.print_log(f"[WARNING] IOC at row number [{value[0]}] Not found on the console, maybe a table refresh is needed.")
                ErrorDialogBox(self, title="IOC not found", message=f"IOC at row number {value[0]} not found on the console, maybe a table refresh is needed?").show()
