import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """Sets up the logger for the application.

    Args:
        app: The Flask application instance.
    """
    logs_dir = os.path.join(app.root_path, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    log_file = os.path.join(logs_dir, "app.log")
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO

    logger = logging.getLogger("flask_app")
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024 * 1024 * 10, backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    app.logger = logger

    return logger
