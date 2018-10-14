#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：Wayne


import csv
import re
from lxml.html import fromstring


class CsvCallback:
    def __init__(self):
        self.writer = csv.writer(open('/home/wayne/waynescraping/data/countries_or_districts.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country_or_district', 'capital',
                       'continent', 'tld', 'currency_code', 'currency_name',
                       'phone', 'postal_code_format', 'postal_code_regex',
                       'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            tree = fromstring(html)
            all_rows = []
            for field in self.fields:
                infoList = tree.xpath('//tr[@id="places_%s__row"]/td[@class="w2p_fw"]' % field)
                if infoList:
                    infoStr = infoList[0].text_content()
                    all_rows.append(infoStr)
            self.writer.writerow(all_rows)
