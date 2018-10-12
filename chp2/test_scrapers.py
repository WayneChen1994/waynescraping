#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


import time
import re
from chp2.all_scrapers import re_scraper, bs_scraper, lxml_scraper, lxml_xpath_scraper
from chp1.advanced_link_crawler import download


NUM_ITERATIONS = 1000   # 测试每个爬虫的时间数
html = download('http://example.python-scraping.com/places/default/view/United-Kingdom-233')


scrapers = [
    ('Regular expressions', re_scraper),
    ('BeautifulSoup', bs_scraper),
    ('Lxml', lxml_scraper),
    ('Xpath', lxml_xpath_scraper)]


for name, scraper in scrapers:
    # 记录开始爬取的时间
    start = time.time()
    for i in range(NUM_ITERATIONS):
        if scraper == re_scraper:
            # 清除缓存
            re.purge()
        result = scraper(html)
        # 检查爬取的结果是否是所期待的
        assert result['area'] == '244,820 square kilometres'
    # 记录爬取结束时间并输出结果
    end = time.time()
    print('%s: %.2f seconds' % (name, end - start))
