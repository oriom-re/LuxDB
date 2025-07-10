import logging
import os

# Konfiguracja loggera core
log_path = os.path.join(os.path.dirname(__file__), 'core.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

logger = logging.getLogger("lux_core")

def start_logger():
    # Tu można zaimplementować logikę startu loggera
    return {"logger": "started"}

def log_event(level, message):
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "critical":
        logger.critical(message)
    else:
        logger.debug(message)
    return {"logged": True, "level": level, "message": message}
