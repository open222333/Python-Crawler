from . import logger
from traceback import format_exc
from fake_useragent import FakeUserAgent
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import sys
import os
import re


class Crawler:

    def __init__(self, url) -> None:
        self.url = url

        ua = FakeUserAgent()
        self.ua = ua.random

        self.all_pages = []

        try:
            self.response = requests.get(self.url)
            self.soup = BeautifulSoup(self.response.text, 'lxml')
        except Exception as err:
            logger.error(f'{err}\n{format_exc()}')

    def get_last_page_num(self, selector: str):
        """取得最後頁面的值

        Args:
            selector (str): 那個值 css selector

        Returns:
            _type_: 若有值則回傳 數字
        """
        try:
            last_num = int(self.soup.select_one(selector).text)
            logger.debug(f'get_last_page_num selector: {selector}\nresult: {last_num}')
            return last_num
        except Exception as err:
            logger.error(f'{err}\n{format_exc()}\nplease check selector: {selector}')

    def set_all_pages(self, page_format: str):
        for i in range(1, self.get_last_page_num()):
            self.all_pages.append(f'{self.url}{page_format.format(i)}')


class MonsnodeCrawler(Crawler):

    def __init__(self, url: str, dir_path: str) -> None:
        """初始化

        Args:
            url (str): 目標網址
            dir_path (str): 資料夾位置
        """
        self.dir_path = dir_path
        super().__init__(url)

    def get_all_urls(self):
        urls = []

        try:
            items = self.soup.select('#scroll > div.op')
            for item in items:
                url = item.select_one('a:nth-child(1)').attrs['href']
                account = item.select_one('a:nth-child(1) > span').text
                if re.search(r'[a-zA-z]+://[^\s]*', url):
                    urls.append({'account': account, 'url': url})
        except Exception as err:
            logger.error(err)

        logger.debug(urls)
        return urls

    def download_file(self, url: str, file_path: str, print_bar=False, chunk_size=1024000):
        """斷點續傳下載檔案

        Args:
            url (str): 網址
            file_path (str): 檔案位置
            print_bar (bool, optional): 顯示進度條. Defaults to False.
            chunk_size (int, optional): 下載chunk大小. Defaults to 1024000.

        Returns:
            bool: 是否下載成功
        """
        # 解析已下載的大小
        if os.path.exists(file_path):
            # 如果存在 斷點續傳
            try:
                file_size = os.path.getsize(file_path)
                open_file_mode = 'ab'
                r_first = requests.get(url)
                remote_file_size = int(r_first.headers.get('content-length'))
                if remote_file_size < file_size:
                    # 檔案大小異常 重載
                    os.remove(file_path)
                    open_file_mode = 'wb'
                    file_size = 0
                elif remote_file_size == file_size:
                    # 已是完成下載的檔案
                    return True
                bpct = True  # 斷點續傳
            except Exception as err:
                logger.error(err)
                os.remove(file_path)
                return False
        else:
            # 如果不存在 非斷點續傳
            open_file_mode = 'wb'
            file_size = 0
            bpct = False  # 非斷點續傳

        if bpct:
            headers = {'Range': f'bytes={file_size}-'}
            r = requests.get(url, stream=True, timeout=15, headers=headers)
            total = r.headers.get('content-length')
            if r.status_code != 206:
                logger.debug(f"不支援斷點下載 刪除後重載:{file_path} code:{r.status_code}")
                os.remove(os.path.dirname(file_path))
                r.raise_for_status()
                return False

            if r.status_code == 404:
                logger.warning(f'code 404 url:{url}')
        else:
            r = requests.get(url, stream=True, timeout=15)
            total = r.headers.get('content-length')
            logger.debug(f'非斷點續傳 code:{r.status_code}')

            if r.status_code == 404:
                logger.warning(f'code 404 url:{url}')

        bar = ProgressBar()
        bar.title = os.path.basename(file_path)

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
            open_file_mode = 'wb'

        with open(file_path, open_file_mode) as f:
            count = 0
            if print_bar:
                try:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if count == 0:
                            done = len(chunk) + file_size
                        else:
                            done = len(chunk)
                        bar(int(total) + file_size, done, in_loop=True)
                        f.write(chunk)
                        count += 1
                except Exception as err:
                    logger.error(err)
            else:
                try:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                except Exception as err:
                    logger.error(err)
        return True

    def __parse_page(self, item):
        try:
            r = requests.get(item['url'])
            soup = BeautifulSoup(r.text, 'lxml')
            twitter_account = soup.select_one('body > div:nth-child(2) > div:nth-child(2) > div:nth-child(5) > b')
            path = soup.select_one('body > div:nth-child(2) > div:nth-child(1) > a:nth-child(1)').attrs['href']
            redirect_url = f'https://monsnode.com/{path}'
            logger.debug(f'{item["url"]}\ntwitter account: {twitter_account}\nredirect url: {redirect_url}')
        except Exception as err:
            logger.error(err)

        try:
            r = requests.get(redirect_url)
            soup = BeautifulSoup(r.text, 'lxml')
            video_url = soup.select_one('body > div:nth-child(2) > strong > a').attrs['href']
            logger.debug(f'{item["url"]}\nvideo url: {video_url}')
            item['video_url'] = video_url
        except Exception as err:
            logger.error(err)

        try:
            video_name = os.path.basename(urlparse(video_url).path)
            item['video_name'] = video_name
        except Exception as err:
            logger.error(err)

        return item

    def parse(self):
        all_items = self.get_all_urls()

        for item in all_items:
            try:
                item = self.__parse_page(item)
                sub_dir = f'{self.dir_path}/(@{item["account"]})'

                if not os.path.exists(sub_dir):
                    os.makedirs(sub_dir)

                self.download_file(item['video_url'], file_path=f'{sub_dir}/{item["video_name"]}', print_bar=True)
            except Exception as err:
                logger.error(err)


class ProgressBar():
    '''進度條'''

    def __init__(self, title='Progress', symbol='=', bar_size=50) -> None:
        """

        Args:
            title (str, optional): 名稱. Defaults to 'Progress'.
            symbol (str, optional): 進度條圖案. Defaults to '='.
            bar_size (int, optional): 進度條長度. Defaults to 50.
        """
        self.title = title
        self.symbol = symbol
        self.bar_size = bar_size
        self.done = 0  # 迴圈內 使用

    def __call__(self, total: int, done=1, decimal=1, in_loop=False):
        """進度條

        Args:
            total (int): 總數
            done (int, optional): 已完成. Defaults to 1.
            decimal (int, optional): 每次完成. Defaults to 1.
            in_loop (bool, optional): 是否在迴圈內. Defaults to False.
        """
        if in_loop:
            self.done += done
            if self.done >= total:
                self.done = total
            self.__print_progress_bar(self.done, total, decimal)
            if self.done == total:
                self.__done()
        else:
            count = 0
            while True:
                count += done
                if count >= total:
                    count = total
                self.__print_progress_bar(count, total, decimal)
                if count == total:
                    break
            self.__done()

    def __print_progress_bar(self, done: int, total: int, decimal: int):
        """繪製 進度表

        Args:
            done (int): 完成數
            total (int): 總任務數
            decimal (int): 百分比顯示到後面幾位
        """
        # 計算百分比
        precent = float(round(100 * done / total, decimal))
        done_symbol = int(precent / 100 * self.bar_size)
        left = self.symbol * done_symbol
        right = ' ' * (self.bar_size - done_symbol)
        # 顯示進度條
        bar = f"\r{self.title}:[{left}{right}] {format(precent, f'.{decimal}f')}% {done}/{total}"
        sys.stdout.write(bar)
        sys.stdout.flush()

    def __done(self):
        print()
