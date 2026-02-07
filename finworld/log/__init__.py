import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("finworld")

class LogLevel:
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

YELLOW_HEX = "#d4b702"

class Logger:
    def __init__(self, *args, **kwargs):
        pass
