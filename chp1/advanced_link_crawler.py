#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


import re
# import itertools
import urllib.request
from urllib import robotparser
from urllib.parse import urljoin
from urllib.error import URLError, HTTPError, ContentTooShortError
from chp1.throttle import Throttle


# def download(url):
#     return urllib.request.urlopen(url).read()


# def download(url):
#     print('Downloading:', url)
#     try:
#         html = urllib.request.urlopen(url).read()
#     except (URLError, HTTPError, ContentTooShortError) as e:
#         print('Download error:', e.reason)
#         html = None
#     return html


# def download(url, num_retries=2):
#     print('Downloading:', url)
#     try:
#         html = urllib.request.urlopen(url).read()
#     except (URLError, HTTPError, ContentTooShortError) as e:
#         print('Download error:', e.reason)
#         html = None
#         if num_retries > 0:
#             if hasattr(e, 'code') and 500 <= e.code < 600:
#                 # 递归重试5xx的HTTP错误
#                 return download(url, num_retries - 1)
#     return html


# def download(url, user_agent='wswp', num_retries=2):
#     print('Downloading:', url)
#     request = urllib.request.Request(url)
#     request.add_header('User-agent', user_agent)
#     try:
#         html = urllib.request.urlopen(request).read()
#     except (URLError, HTTPError, ContentTooShortError) as e:
#         print('Download error:', e.reason)
#         html = None
#         if num_retries > 0:
#             if hasattr(e, 'code') and 500 <= e.code < 600:
#                 return download(url, num_retries - 1)
#     return html


# def crawl_sitemap(url):
#     # 下载网站地图
#     sitemap = download(url)
#     # 提取网站地图中的链接
#     links = re.findall('<loc>(.*?)</loc>', sitemap)
#     # 下载每一个链接
#     for link in links:
#         html = download(link)
#         # 进行爬取工作
#         # ...


# def crawl_site(url):
#     for page in itertools.count(1):
#         pg_url = '{}{}'.format(url, page)
#         html = download(pg_url)
#         if html is None:
#             break
#         # 成功 - 就能够爬取结果


# def crawl_site(url, max_errors=5):
#     for page in itertools.count(1):
#         pg_url = '{}{}'.format(url, page)
#         html = download(pg_url)
#         if html is None:
#             num_errors += 1
#             if num_errors == max_errors:
#                 # 到达最大错误次数，退出循环
#                 break
#         else:
#             num_errors = 0
#             # 成功 - 就能够爬取结果


def download(url, user_agent='wswp', num_retries=2, charset='utf-8', proxy=None):
    """ HTML网页下载器 """
    print('Downloading:', url)
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)
    try:
        # 代理支持
        if proxy:
            proxy_support = urllib.request.ProxyHandler({'http': proxy})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
        resp = urllib.request.urlopen(request)
        cs = resp.headers.get_content_charset()
        if not cs:
            cs = charset
        html = resp.read().decode(cs)
    except (URLError, HTTPError, ContentTooShortError) as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url=url, user_agent=user_agent, num_retries=num_retries-1, charset=charset, proxy=proxy)
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


def link_crawler(start_url, link_regex, robots_url=None, user_agent='wswp', proxy=None, delay=3, max_depth=4, scrape_callback=None):
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
    data = []
    # 爬虫下载限速
    throttle = Throttle(delay)
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
            html = download(url=url, user_agent=user_agent, proxy=proxy)
            if html is None:
                break
            if scrape_callback:
                data.extend(scrape_callback(url, html) or [])
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
