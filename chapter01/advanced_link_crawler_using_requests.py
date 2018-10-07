#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


import re
import time
import requests
from urllib import robotparser
from urllib.parse import urljoin
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


def download(url, user_agent='wswp', num_retries=2, proxies=None):
    """ 使用requests库实现的HTML下载器 """
    print('Downloading:', url)
    headers = {'User-Agent': user_agent}
    try:
        resp = requests.get(url, headers=headers, proxies=proxies)
        html = resp.text
        if resp.status_code >= 400:
            print('Download error:', resp.text)
            html = None
            if num_retries and 500 <= resp.status_code < 600:
                return download(url=url, num_retries=num_retries-1)
    except requests.exceptions.RequestException as e:
        print('Download error:', e.strerror)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url=url, user_agent=user_agent, num_retries=num_retries-1)
    return html


def get_links(html):
    """
    返回一个由HTML中所有链接为元素组成的列表
    """
    # 一个用于从网页中提取所有链接的正则表达式
    webpage_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
    # 网页上所有链接组成的列表
    return webpage_regex.findall(html)


def get_robots_parser(robots_url):
    """ 传入robots.txt所在URL，返回robots解析器对象 """
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp


def link_crawler(start_url, link_regex, robots_url=None, user_agent='wswp', max_depth=4):
    """
    从给定的起始URL开始爬取所有正则表达式匹配到的链接
    """
    if not robots_url:
        robots_url = '{}/robots.txt'.format(start_url)
    rp = get_robots_parser(robots_url)

    crawl_queue = [start_url]
    # 定义一个set集合保存所有已经爬取过的链接
    # seen = set(crawl_queue)
    # 新的seen为字典，增加了以发现链接的深度记录
    seen = {}
    # 爬虫下载限速
    throttle = Throttle(delay=1)
    while crawl_queue:
        url = crawl_queue.pop()
        # 检查URL是否允许爬取(根据robots.txt文件中的定义)
        if rp.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            # 到达最大深度，不再向队列中添加该网页中的链接
            if depth == max_depth:
                print('Skipping %s due to depth' % url)
                continue
            throttle.wait(url)
            html = download(url=url, user_agent=user_agent)
            if html is None:
                break
            # 在页面HTML中筛选出匹配我们正则表达式的链接
            for link in get_links(html):
                if re.search(link_regex, link):
                    abs_link = urljoin(start_url, link)
                    # 检查是否已经爬取过该链接
                    if abs_link not in seen:
                        # seen.add(abs_link)
                        # 爬取深度增加
                        seen[abs_link] = depth + 1
                        crawl_queue.append(abs_link)
        else:
            print('Blocked by robots.txt:', url)
