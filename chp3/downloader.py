#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


from chp1.throttle import Throttle
from random import choice
import requests


class Downloader:
    def __init__(self, delay=5, user_agent='wswp', proxies=None, cache={}):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = None # 每个请求我们都将设置此属性
        self.cache = cache

    def __call__(self, url, num_retries=2):
        self.num_retries = num_retries
        try:
            result = self.cache[url]
            print('Loaded from cache:', url)
        except KeyError:
            result = None
        if result and self.num_retries and 500 <= result['code'] < 600:
            # 服务器错误所以忽略缓存加载的结果
            # 重新下载
            result = None
        if result is None:
            # 未能从缓存中加载，因此仍然需要下载
            self.throttle.wait(url)
            proxies = choice(self.proxies) if self.proxies else None
            headers = {'User-Agent': self.user_agent}
            result = self.download(url, headers, proxies)
            if self.cache:
                # 将结果保存进缓存中
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxies):
        print('Downloading:', url)
        try:
            resp = requests.get(url, headers=headers, proxies=proxies)
            html = resp.text
            if resp.status_code >= 400:
                print('Download error:', resp.text)
                html = None
                if self.num_retries and 500 <= resp.status_code < 600:
                    self.num_retries -= 1
                    return self.download(url, headers, proxies)
        except requests.exceptions.RequestException as e:
            print('Download error:', e)
            return {'html': None, 'code': 500}
        return {'html': html, 'code': resp.status_code}
