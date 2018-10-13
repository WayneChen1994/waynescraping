#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


import re
import urllib.request
from urllib import robotparser
from urllib.parse import urljoin
from urllib.error import URLError, HTTPError, ContentTooShortError
from lxml.html import fromstring
from chp1.throttle import Throttle


def download(url, num_retries=2, user_agent='wswp', charset='utf-8', proxy=None):
    print('Downloading:', url)
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)
    try:
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
        print('Download error:', e)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, num_retries - 1)
    return html


def get_robots_parser(robots_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp


def get_links(html):
    webpage_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
    return webpage_regex.findall(html)


def scrape_callback(url, html):
    """ 使用XPath和lxml从国家（或地区）数据中抓取每一行 """
    fields = ('area', 'population', 'iso', 'country_or_district', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')

    if re.search('/view/', url):
        tree = fromstring(html)
        all_rows = [
            tree.xpath('//tr[@id="places_%s__row"]/td[@class="w2p_fw"]' % field)[0].text_content()
            for field in fields]
        print(url, all_rows)


def link_crawler(start_url, link_regex, robots_url=None, user_agent='wswp', proxy=None, delay=3, max_depth=4, scrape_callback=None):
    crawl_queue = [start_url]
    seen = {}
    data = []

    if not robots_url:
        robots_url = '{}/robots.txt'.format(start_url)
    rp = get_robots_parser(robots_url)

    throttle = Throttle(delay)

    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                print('Skipping %s due to depth' % url)
                continue

            throttle.wait(url)

            html = download(url, user_agent=user_agent, proxy=proxy)

            if not html:
                continue

            if scrape_callback:
                data.extend(scrape_callback(url, html) or [])

            for link in get_links(html):
                if re.search(link_regex, link):
                    abs_link = urljoin(start_url, link)
                    if abs_link not in seen:
                        seen[abs_link] = depth + 1
                        crawl_queue.append(abs_link)
        else:
            print('Blocked by robots.txt:', url)
