import logging
from rss_reader.config_loader import log_path

def setup_logger(name="rss_logger", log_file=log_path, level=logging.INFO):
    """
    Set up a logger with both file and console output.

    Args:
        name (str): Name of the logger instance.
        log_file (str): Path to the log file.
        level (int): Logging level (e.g., DEBUG, INFO, WARNING).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding multiple handlers if logger already has them
    if not logger.handlers:
        # File handler: logs messages to a file
        fh = logging.FileHandler(log_file)
        # Stream handler: logs messages to console
        ch = logging.StreamHandler()

        # Set a common format for both handlers
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Attach handlers to logger
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger

# Initialize the logger instance for use throughout the app
logger = setup_logger()
