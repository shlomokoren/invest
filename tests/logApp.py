import logging

# Configure the logging level, format, and output
logging.basicConfig(
    level=logging.INFO,  # Set the lowest level (DEBUG) to capture all messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Logs to a file
        logging.StreamHandler()          # Logs to console
    ]
)

# Log messages at different levels
logging.debug("This is a DEBUG message")
logging.info("This is an INFO message")
logging.warning("This is a WARNING message")
logging.error("This is an ERROR message")
logging.critical("This is a CRITICAL message")
