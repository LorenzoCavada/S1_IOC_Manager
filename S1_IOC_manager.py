import tkinter
import customtkinter

from gui import ViewerAppWindow
from utils.log_handler import logger

if __name__ == "__main__":
    logger.print_log("[INFO] Starting S1_IOC_manager v1")
    app = ViewerAppWindow()
    app.mainloop()
