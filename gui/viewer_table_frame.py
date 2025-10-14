import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from dateutil import parser
from datetime import datetime
import json

from utils.log_handler import logger

from gui.custom_messagebox import YesNoDialogBox, InfoDialogBox, ErrorDialogBox, YesNoTextDialogBox

from data import get_s1_ioc_by_value, delete_s1_ioc_by_value, disable_s1_ioc_by_value, enable_s1_ioc_by_value

colums_settings = {
    'num': {'allignment': tk.CENTER, 'size': 60},
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
    def __init__(self, parent, value, data, ioc_disabled):
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
        
        # Frame for buttons (bottom row)
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side=tk.BOTTOM, pady=10)

        self.delete_ioc_button = ctk.CTkButton(button_frame, text="Delete IOC 🗑️", fg_color="red", hover_color="red3", command=lambda: (self._delete_ioc(data)))
        self.delete_ioc_button.pack(side=tk.LEFT, padx=10)

        if not ioc_disabled:
            self.disable_ioc_button = ctk.CTkButton(button_frame, text="Disable IOC 🚫", fg_color="orange", hover_color="orange3", command=lambda: (self._disable_ioc(data)))
            self.disable_ioc_button.pack(side=tk.LEFT, padx=10)
        else:
            self.enable_ioc_button = ctk.CTkButton(button_frame, text="Enable IOC ✅", fg_color="green", hover_color="green3", command=lambda: (self._enable_ioc(data)))
            self.enable_ioc_button.pack(side=tk.LEFT, padx=10)

    def show(self):
        self.wait_window()

    def _enable_ioc(self, data):
        data = json.loads(data)[0]
        logger.print_log(f"[INFO] User want to enable IOC with value: [{data['value']}]. Asking for confirmation.")

        user_choice = YesNoDialogBox(self, title="Are you sure?", message=f"Do you want to enable the IOC with value: [{data['value']}] from SentinelOne?")
        user_choice = user_choice.show()

        if user_choice:
            logger.print_log(f"[INFO] User want to enable IOC with value: [{data['value']}].")

            result = enable_s1_ioc_by_value(data['value'], "[ALLITUDE] IOC Exclusion List")

            if result:
                InfoDialogBox(self, title = "IOC enabled", message=f"The IOC [{data['value']}] has been successfully enabled.\nRemember to refresh the table!").show()
                self.destroy()
            else:
                ErrorDialogBox(self, title="IOC enabled", message=f"The IOC [{data['value']}] has NOT been successfully enabled.").show()
        else:
            logger.print_log(f"[INFO] User don't want to enable IOC with value: [{data['value']}]. Moving on.")

    def _delete_ioc(self, data):
        data = json.loads(data)[0]
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
    
    def _disable_ioc(self, data):
        data = json.loads(data)[0]
        logger.print_log(f"[INFO] User want to disable IOC with value: [{data['value']}]. Asking for confirmation.")

        dlg = YesNoTextDialogBox(self, title="Are you sure?", message=f"Do you want to disable the IOC with value: [{data['value']}] from SentinelOne?")
        user_choice, description = dlg.show()

        if user_choice:
            logger.print_log(f"[INFO] User want to disable IOC with value: [{data['value']}].")

            result = disable_s1_ioc_by_value(data['value'], description)

            if result:
                InfoDialogBox(self, title = "IOC disabled", message=f"The IOC [{data['value']}] has been successfully disabled.\nRemember to refresh the table!").show()
                self.destroy()
            else:
                ErrorDialogBox(self, title="IOC disabled", message=f"The IOC [{data['value']}] has NOT been successfully disabled.").show()
        else:
            logger.print_log(f"[INFO] User don't want to disabled IOC with value: [{data['value']}]. Moving on.")

class ViewerTableFrame(tk.Frame):
    def __init__(self, parent, data, disabled_indicators):
        super().__init__(parent)
        self.tree = None
        self.sort_state = {}   # Track sort order for each column
        self.original_headings = {}  # Keep original column names
        self.build_table(data, disabled_indicators)

        # Let this frame expand with its parent
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def build_table(self, data, disabled_indicators=[]):
        logger.print_log("[INFO] Building the IOC table.")

        # Create Treeview
        self.tree = ttk.Treeview(self, columns=list(data[0].keys()), show="headings")

        # Configure columns and headings
        for col in data[0].keys():
            heading = col
            self.original_headings[col] = heading  # store original name
            alignment = colums_settings[col].get("allignment", tk.CENTER)
            width = colums_settings[col].get("size", None)

            stretch = width is None

            # Bind sorting command on column header
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, anchor=alignment, stretch=stretch, width=width if width else 100)

            self.tree.tag_configure("red", background="#ffcccc")
            self.tree.tag_configure("normal", background="white")


        # Insert rows
        for row in data:
            row['creationTime'] = parser.parse(row['creationTime']).strftime("%d/%m/%Y %H:%M:%S") if row.get('creationTime') else ""
            row['updatedAt']    = parser.parse(row['updatedAt']).strftime("%d/%m/%Y %H:%M:%S")    if row.get('updatedAt') else ""
            row['validUntil']   = parser.parse(row['validUntil']).strftime("%d/%m/%Y %H:%M:%S")   if row.get('validUntil') else ""
            
            # In case the ioc is inserted as critical, paint the row in red
            if row['value'] in disabled_indicators:
                self.tree.insert("", "end", values=list(row.values()), tags=("red",))
            else:
                self.tree.insert("", "end", values=list(row.values()), tags=("normal",))

        # Create scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)

        # Attach scrollbars to tree
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout with grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Make frame expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind double click
        self.tree.bind("<Double-1>", self.row_double_click)

    def sort_column(self, col, reverse):
        """Sort a column and update header indicator."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        def try_parse(val):
            """Try to parse into int, float, datetime, else string."""
            from datetime import datetime
            for parse_fn in (int, float):
                try:
                    return parse_fn(val)
                except Exception:
                    pass
            try:
                return datetime.strptime(val, "%d/%m/%Y %H:%M:%S")
            except Exception:
                return val.lower()  # fallback to string

        # Sort
        items.sort(key=lambda t: try_parse(t[0]), reverse=reverse)

        # Reorder
        for index, (_, k) in enumerate(items):
            self.tree.move(k, '', index)

        # Reset all headers
        for c in self.original_headings:
            self.tree.heading(c, text=self.original_headings[c],
                              command=lambda colname=c: self.sort_column(colname, False))

        # Add arrow to sorted column
        arrow = "▼" if reverse else "▲"
        self.tree.heading(col, text=f"{self.original_headings[col]} {arrow}",
                          command=lambda: self.sort_column(col, not reverse))

        # Save state
        self.sort_state[col] = not reverse

    def row_double_click(self, event):        
        item_id = self.tree.identify_row(event.y)
        if item_id:
            value = self.tree.item(item_id, "values")

            # Check if the row is tagged as disabled
            tags = self.tree.item(item_id, "tags")
            ioc_disabled = False
            if "red" in tags:
                ioc_disabled = True 
            
            logger.print_log(f"[INFO] Double click on item [{value[0]}] detected. Showing detailed pop up window.")

            ioc_data = get_s1_ioc_by_value(value[4])            
            if ioc_data is not None:
                ioc_data = json.dumps(ioc_data, indent=2)
                item_window = ItemWindow(self, value=value, data=ioc_data, ioc_disabled=ioc_disabled)
                item_window.show()
            else:
                logger.print_log(f"[WARNING] IOC at row number [{value[0]}] Not found on the console, maybe a table refresh is needed.")
                ErrorDialogBox(self, title="IOC not found",
                               message=f"IOC at row number {value[0]} not found on the console, maybe a table refresh is needed?").show()
