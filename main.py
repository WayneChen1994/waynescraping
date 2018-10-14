#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


from chp2.advanced_link_crawler import link_crawler
from chp2.csv_callback import CsvCallback


if __name__ == '__main__':
    link_crawler('http://example.python-scraping.com/', '/(index|view)', max_depth=-1, scrape_callback=CsvCallback())
