from configparser import ConfigParser
from datetime import datetime
import logging
import os


config = ConfigParser()
config.read('config/config.ini')

URL = config.get('BASIC', 'URL', fallback='')
PAGE_FORMAT = config.get('BASIC', 'PAGE_FORMAT', fallback='')
DEBUG = config.getboolean('BASIC', 'DEBUG', fallback=False)
LOG_DIR = config.get('BASIC', 'LOG_DIR', fallback='log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LAST_PAGE_NUM_SELECTOR = config.get('SELECTOR', 'LAST_PAGE_NUM_SELECTOR', fallback='')
ITEMS_SELECTOR = config.get('SELECTOR', 'ITEMS_SELECTOR', fallback='')

# 設置logger路徑
log_file = f'{LOG_DIR}/{datetime.now().__format__("%Y%m%d")}.log'

logger = logging.getLogger('main')
log_handler = logging.FileHandler(log_file)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_format)
if DEBUG:
    log_handler.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
