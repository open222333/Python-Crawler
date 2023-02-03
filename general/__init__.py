from configparser import ConfigParser
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import logging
import os


config = ConfigParser()
config.read('config/config.ini')

URL = config.get('BASIC', 'URL', fallback='')
# 頁面網址格式 $URL$PAGE_FORMAT
PAGE_FORMAT = config.get('BASIC', 'PAGE_FORMAT', fallback='')

DIR = config.get('BASIC', 'DIR', fallback='download')

# log資料夾
LOG_DIR = config.get('LOG', 'LOG_DIR', fallback='logs')
# 關閉log
DISABLE_LOG = config.get('LOG', 'DISABLE_LOG', fallback=False)
# 指定log等級 預設debug
LOG_LEVEL = config.get('LOG', 'LOG_LEVEL', fallback='WARNING')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LAST_PAGE_NUM_SELECTOR = config.get('SELECTOR', 'LAST_PAGE_NUM_SELECTOR', fallback='')
ITEMS_SELECTOR = config.get('SELECTOR', 'ITEMS_SELECTOR', fallback='')

# 設置logger路徑
log_file = f'{LOG_DIR}/{datetime.now().__format__("%Y%m%d")}.log'

logger = logging.getLogger('main')

if LOG_LEVEL == 'DEBUG':
    logger.setLevel(logging.DEBUG)
elif LOG_LEVEL == 'INFO':
    logger.setLevel(logging.INFO)
elif LOG_LEVEL == 'WARNING':
    logger.setLevel(logging.WARNING)
elif LOG_LEVEL == 'ERROR':
    logger.setLevel(logging.ERROR)
elif LOG_LEVEL == 'CRITICAL':
    logger.setLevel(logging.CRITICAL)

log_handler = TimedRotatingFileHandler(log_file, when='D', backupCount=7)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_format)
logger.addHandler(log_handler)

if DISABLE_LOG:
    logging.disable(logging.CRITICAL)
