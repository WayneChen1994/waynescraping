#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


import time
from urllib.parse import urlparse


class Throttle:
    """ 对同一域名的下载请求之间添加延时 """
    def __init__(self, delay):
        # 指定每个域名的下载间隔延迟量
        self.delay = delay
        # 保存上次访问域名的时间戳
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (time.time() - last_accessed)
            if sleep_secs > 0:
                # 说明该域名最近被访问过，所以需要睡眠
                time.sleep(sleep_secs)
        # 更新最后访问的时间
        self.domains[domain] = time.time()
