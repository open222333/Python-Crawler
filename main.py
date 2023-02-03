from general.crawler import MonsnodeCrawler
from general import URL, DISABLE_LOG, LOG_DIR, LOG_LEVEL, DIR
from pprint import pprint
import re


setting_info = {
    'log紀錄功能': not DISABLE_LOG
}

if not DISABLE_LOG:
    setting_info['log位置'] = LOG_DIR
    setting_info['log等級'] = LOG_LEVEL

pprint(setting_info)

if re.search(r'monsnode.com', URL):
    mc = MonsnodeCrawler(URL, DIR)
    mc.parse()