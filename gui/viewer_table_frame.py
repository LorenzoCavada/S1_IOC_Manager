import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json

from utils.log_handler import logger

from gui.item_window import ItemWindow
from gui.custom_messagebox import ErrorDialogBox
from data import get_s1_ioc_by_value

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

class ViewerTableFrame(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.tree = None
        self.build_table(data)
        self.pack_propagate(False)

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
            # Formatting date in format "dd/mm/yyyy hh:mm:ss". If no date is present a blank value is added
            row['creationTime'] = (datetime.strptime(row['creationTime'], "%Y-%m-%dT%H:%M:%S.%fZ")).strftime("%d/%m/%Y %H:%M:%S") if row['creationTime'] != None else ""
            row['updatedAt'] = (datetime.strptime(row['updatedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")).strftime("%d/%m/%Y %H:%M:%S") if row['updatedAt'] != None else ""
            row['validUntil'] = (datetime.strptime(row['validUntil'], "%Y-%m-%dT%H:%M:%S.%fZ")).strftime("%d/%m/%Y %H:%M:%S") if row['validUntil'] != None else ""
            self.tree.insert("", "end", values=list(row.values()))
            self.tree.bind("<Double-1>", self.row_double_click)

        self.tree.pack(fill="both", expand=True)
    
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
