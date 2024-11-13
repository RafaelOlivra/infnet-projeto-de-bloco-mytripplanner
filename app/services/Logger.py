import os
import logging
import json

from logging.handlers import RotatingFileHandler
from datetime import datetime

from services.AppData import AppData


class SimpleLogger:
    def __init__(
        self,
        log_folder=AppData().get_config("log_dir"),
        log_filename="app.log",
        max_size=1_000_000,
        backup_count=5,
    ):
        # Create the log folder if it does not exist
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Define the full log file path
        log_path = os.path.join(log_folder, log_filename)

        # Set up logging with file rotation
        self.logger = logging.getLogger("SimpleLogger")
        self.logger.setLevel(logging.DEBUG)

        # Create a rotating file handler
        handler = RotatingFileHandler(
            log_path, maxBytes=max_size, backupCount=backup_count
        )

        # Define the log format
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

    def log_info(self, message, obj=None):
        self._log_with_object(logging.INFO, message, obj)

    def log_warning(self, message, obj=None):
        self._log_with_object(logging.WARNING, message, obj)

    def log_error(self, message, obj=None):
        self._log_with_object(logging.ERROR, message, obj)

    def log_debug(self, message, obj=None):
        self._log_with_object(logging.DEBUG, message, obj)

    def _log_with_object(self, level, message, obj):
        # Convert the object to a string if it exists, using JSON if possible
        if obj is not None:
            try:
                obj_str = json.dumps(
                    obj, default=str
                )  # Use default=str to handle non-serializable objects
            except TypeError:
                obj_str = repr(obj)  # Fallback to repr if JSON serialization fails
            message = f"{message} | Object: {obj_str}"

        # Log the message at the specified level
        if level == logging.INFO:
            self.logger.info(message)
        elif level == logging.WARNING:
            self.logger.warning(message)
        elif level == logging.ERROR:
            self.logger.error(message)
        elif level == logging.DEBUG:
            self.logger.debug(message)
