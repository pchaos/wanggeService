# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_HSGTCG.py

Description :

@Author :       pchaos

date：          18-5-30
-------------------------------------------------
Change Activity:
               18-5-30:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import HSGTCG

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd

__author__ = 'pchaos'

def str2Float(astr):
    """ 包含汉字数字的字符串转为float

    :param astr:
    :return:
    """
    try:
        if type(astr) is str:
            y = '亿'
            if astr.find(y) >= 0:
                return float(astr.replace(y, '')) * 100000
    except:
        return 0

class TestHSGTCG(TestCase):
    def test_getlist(self):
        self.fail()

    def test_scrapt(self):
        """ 个股北向持股

        :return:
        """
        code = '600066'
        url = 'http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}'.format(code)

        opts = Options()
        opts.set_headless()
        assert opts.headless  # operating in headless mode
        browser = webdriver.Firefox()

        try:
            browser.get(url)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            table = soup.find_all(id='tb_cgtj')[0]
            df = pd.read_html(str(table), header=1)[0]
            df.columns = ['date', 'related', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday', 'fiveday', 'tenday']
            for i in df.index:
                v= df.iloc[i]
                print('{} {} {} {}'.format(v.close, v.hvol, v.hamount, v.hpercent))
                HSGTCG.objects.get_or_create(code=code, close=v.close, hvol=str2Float(v.hvol), hamount=str2Float(v.hamount), hpercent=v.hpercent)
        finally:
            if browser:
                browser.close()
        hsgtcg = HSGTCG.getlist(code)
        # hsgtcg = HSGTCG.getlist()
        print(hsgtcg)
        self.assertTrue(hsgtcg.count() > 10, '保存的数量： {}'.format(hsgtcg.count()))


    def test_StockStatistics(self):
        """ 北持股向市值大于八千万

        :return:
        """