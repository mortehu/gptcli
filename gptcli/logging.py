import logging
import sys
from datetime import datetime

class CustomFormatter(logging.Formatter):
    ANSI_YELLOW = "\033[33;1m"
    ANSI_RED = "\033[31;1m"
    ANSI_RESET = "\033[0m"

    def format(self, record):
        level = record.levelname
        iso_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z'  # ISO 8601 format
        msg = super().format(record)

        if level == "WARNING":
            return f"{iso_time} {self.ANSI_YELLOW}WARN:{self.ANSI_RESET} {msg}"
        elif level == "ERROR":
            return f"{iso_time} {self.ANSI_RED}ERROR:{self.ANSI_RESET} {msg}"
        else:
            return f"{iso_time} {msg}"

def setup():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers, if any
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create a console handler and set its logging level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Set the formatter for the console handler
    formatter = CustomFormatter('%(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the root logger
    root_logger.addHandler(console_handler)
