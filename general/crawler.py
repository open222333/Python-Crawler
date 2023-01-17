from . import PAGE_FORMAT, LAST_PAGE_NUM_SELECTOR, ITEMS_SELECTOR
from . import logger
from traceback import format_exc
from fake_useragent import FakeUserAgent
from bs4 import BeautifulSoup
import requests


class Crawler:

    def __init__(self, url) -> None:
        self.url = url

        ua = FakeUserAgent()
        self.ua = ua.random

        self.all_pages = []

        r = requests.get(self.url)
        self.soup = BeautifulSoup(r.text, 'lxml')

    def get_last_page_num(self):
        try:

            last_num = int(self.soup.select_one(LAST_PAGE_NUM_SELECTOR).text)
            logger.debug(f'get_last_page_num selector: {LAST_PAGE_NUM_SELECTOR}\nresult: {last_num}')
            return last_num
        except:
            logger.error(f'get_last_page_num error\n{format_exc()}\nplease check selector: {LAST_PAGE_NUM_SELECTOR}')

    def set_all_pages(self):
        for i in range(1, self.get_last_page_num()):
            self.all_pages.append(f'{self.url}{PAGE_FORMAT.format(i)}')

    def prase(self):
        pass
