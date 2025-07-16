from datetime import datetime
from config.config_loader import config

class Colors: # You may need to change color settings
    RED = '\033[31m'
    ENDC = '\033[m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'

    @staticmethod
    def print_warning(text:str):
        print(f"{Colors.YELLOW}{text}{Colors.ENDC}")

    @staticmethod
    def print_error(text:str):
        print(f"{Colors.RED}{text}{Colors.ENDC}")

    @staticmethod
    def print_debug(text:str):
        print(f"{Colors.BLUE}{text}{Colors.ENDC}")

    @staticmethod
    def print_success(text:str):
        print(f"{Colors.GREEN}{text}{Colors.ENDC}")

    @staticmethod  
    def print_info(text:str):
        print(f"{text}")
    

class Logger:
    def __init__(self):
        self.log_file = open("./S1_IOC_manager.log", "w")
    
    def print_log(self, message:str):
        if config.debug:
            message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
            
            if("INFO" in message):
                Colors.print_info(message)
            elif("ERROR" in message):
                Colors.print_error(message)
            elif("SUCCESS" in message):
                Colors.print_success(message)
            elif("WARNING" in message):
                Colors.print_warning(message)
            else:
                Colors.print_debug(message)

            self.log_file = open("./S1_IOC_manager.log", "a")
            self.log_file.write(f"{message}\n")
            self.log_file.close()

logger = Logger()