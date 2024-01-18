import logging
import colorama
from colorama import Fore

# Initialize Colorama
colorama.init(autoreset=True)


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.GREEN,
        "INFO": Fore.WHITE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.LIGHTMAGENTA_EX,
    }

    def __init__(self):
        # Adjust the formatting here to ensure consistent alignment
        log_fmt = "%(asctime)s.%(msecs)03d: [%(levelname)s]\t %(message)s"
        self.formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record):
        return self.COLORS.get(record.levelname, "") + self.formatter.format(record)


# Configure the basic settings for logging
logging.basicConfig(level=logging.INFO)

# Apply color formatter to all handlers
for handler in logging.root.handlers:
    handler.setFormatter(ColorFormatter())


# create logger
logger = logging.getLogger(__name__)
