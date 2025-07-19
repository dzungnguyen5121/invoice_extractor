import json
import logging
from logging.handlers import RotatingFileHandler

def load_config(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {config_file}: {e}")
        return {'default': {}}

def setup_logger(log_file='invoices.log', max_bytes=5*1024*1024, backup_count=5):
    logger = logging.getLogger(__name__)
    log_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
    log_handler.setLevel(logging.INFO)
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)
    if not logger.hasHandlers():
        logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    logging.getLogger("pdfminer").setLevel(logging.WARNING)
    logging.getLogger("pdfplumber").setLevel(logging.WARNING)
    return logger 