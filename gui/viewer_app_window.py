import csv

import tkinter as tk
import customtkinter as ctk

from gui.viewer_table_frame import ViewerTableFrame
from gui.uploader_app_window import UploaderAppWindow
from gui.custom_messagebox import ErrorDialogBox, InfoDialogBox

from data import get_s1_ioc, get_s1_filtered_ioc

from utils.log_handler import logger 

ctk.set_default_color_theme("dark-blue")  # Optional theme enhancement
ctk.set_appearance_mode("light")         # Adapts to user's light/dark mode

class ViewerAppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("S1 IOC Manager")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        logger.print_log(f"[INFO] Generating the canvas. Screen size [{screen_width}x{screen_height}]")

        self.geometry(f'{screen_width}x{screen_height}')
        self.maxsize(1800, 900)

        # Configure root grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Table should expand

        # --- Top Search Area ---
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=1)

        # Left side: Upload button
        self.upload_button = ctk.CTkButton(search_frame, text="Upload IOC 📝", width=200, command=self.upload_ioc)
        self.upload_button.grid(row=0, column=0, sticky="w")

        # Right side: Search UI
        right_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e")

        self.search_entry = ctk.CTkEntry(right_frame, placeholder_text="Filter Value", width=300)
        self.search_entry.grid(row=0, column=0, padx=5)

        self.search_type = ctk.CTkOptionMenu(right_frame, values=["Value", "User", "Name", "Description"], width=130)
        self.search_type.grid(row=0, column=1, padx=5)

        self.search_button = ctk.CTkButton(right_frame, text="Search 🔍", width=80, command=self.search_ioc)
        self.search_button.grid(row=0, column=2, padx=5)

        # --- Table Area ---
        logger.print_log("[INFO] Preparing the first IOC table.")
        self.table = ViewerTableFrame(self, get_s1_ioc())
        self.table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Bottom Button Area ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        bottom_frame.grid_columnconfigure(1, weight=0)  # Center button
        bottom_frame.grid_columnconfigure(2, weight=1)  # Right button

        self.get_ioc_button = ctk.CTkButton(bottom_frame, text="Grab some fresh IOC ✊", command=self.show_table)
        self.get_ioc_button.grid(row=0, column=1)

        self.extra_button = ctk.CTkButton(bottom_frame, text="Export 📤", width=80, command=self.export_data)
        self.extra_button.grid(row=0, column=2, sticky="e", padx=(0, 5))

    def export_data(self):
        logger.print_log("[INFO] Exporting current table.")
        search_value = self.search_entry.get()
        search_type = self.search_type.get()

        logger.print_log("[INFO] Checking if any filter is applied.")
        if search_value != "":
            logger.print_log("[INFO] Filter are applied. Getting the same set of IOC.")
            ioc_dump = get_s1_filtered_ioc(search_value, search_type)
        else:
            logger.print_log("[INFO] Filter are not applied. Getting a fresh new set of IOC.")
            ioc_dump = get_s1_ioc()

        if len(ioc_dump) > 0:
            logger.print_log("[INFO] Exporting the table to csv.")
            keys = ioc_dump[0].keys()

            with open('./IOC_Manager_export.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, keys)
                writer.writeheader()
                writer.writerows(ioc_dump)
            
            InfoDialogBox(self, title=f"Export completed", message=f"IOC_Manager_export.csv file created in the home folder.").show()

            
            logger.print_log("[INFO] IOC export completed.")

        else:
            logger.print_log("[ERROR] Unable to retrieve a valid list of IOC. Cannot export them.")
            ErrorDialogBox(self, title=f"Something went wrong", message=f"Unable to retrieve a valid list of IOC. Cannot export them.").show()


    def show_table(self):
        logger.print_log("[INFO] Updating the IOC table.")

        # Destroy old table
        if self.table:
            self.table.destroy()

        # Create and place new table using grid
        self.table = ViewerTableFrame(self, get_s1_ioc())
        self.table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def search_ioc(self):
        search_value = self.search_entry.get()
        search_type = self.search_type.get()

        logger.print_log(f"[INFO] Updating the IOC table filtered for value: [{search_value}].")

        if search_value.strip() == "":
            logger.print_log(f"[WARNING] User input not found, printing the full table again.")
            self.show_table()
        else:
            if self.table:
                self.table.destroy()
            self.table = ViewerTableFrame(self, get_s1_filtered_ioc(search_value, search_type))
            self.table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    
    def upload_ioc(self):
        logger.print_log("[INFO] S1_IOC_Uploader v.2")
        uploader_window = UploaderAppWindow(self)
        uploader_window.show()
