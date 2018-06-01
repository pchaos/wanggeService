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
from stocks.models import convertToDate
from stocks.models import Stocktradedate

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time , datetime

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
    def setUp(self):
        Stocktradedate.importList()

    def test_getlist(self):
        self.fail()

    def test_scrapt(self):
        """ 个股北向持股

        :return:
        """
        code = '600066'
        code = '000425'
        code = '000792'
        code = '002493'
        url = 'http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}'.format(code)

        browser = webdriver.Firefox()
        browser.maximize_window()
        try:
            browser.get(url)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            table = soup.find_all(id='tb_cgtj')[0]
            df = pd.read_html(str(table), header=1)[0]
            df.columns = ['date', 'related', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday', 'fiveday',
                          'tenday']
            for i in df.index:
                v = df.iloc[i]
                print('{} {} {} {}'.format(v.close, v.hvol, v.hamount, v.hpercent))
                HSGTCG.objects.get_or_create(code=code, close=v.close, hvol=str2Float(v.hvol),
                                             hamount=str2Float(v.hamount), hpercent=v.hpercent, tradedate=convertToDate(v.date))
        finally:
            if browser:
                browser.close()
        hsgtcg = HSGTCG.getlist(code)
        # hsgtcg = HSGTCG.getlist()
        print(hsgtcg)
        self.assertTrue(hsgtcg.count() > 10, '保存的数量： {}'.format(hsgtcg.count()))
        self.assertTrue(isinstance(hsgtcg[0].tradedate,datetime.date))
        self.assertTrue(hsgtcg.filter(tradedate=None).count() == 0)

    def test_importList(self):
        """
        测试保存沪深港通持股
        :return:
        """
        # HSGTCG.importList()
        HSGTCG.importList(firefoxHeadless=False)
        hsgtcg = HSGTCG.getlist()
        print(hsgtcg)
        self.assertTrue(hsgtcg.count() > 10, '保存的数量： {}'.format(hsgtcg.count()))
        print('数据库中保存的记录数量：{}'.format(hsgtcg.count()))

    def test_importListdup(self):
        """
        测试保存沪深港通持股
        :return:
        """
        # HSGTCG.importList()
        HSGTCG.importList(firefoxHeadless=False)
        hsgtcg = HSGTCG.getlist()
        print(hsgtcg)
        self.assertTrue(hsgtcg.count() > 1000, '保存的数量： {}'.format(hsgtcg.count()))
        print('数据库中保存的记录数量：{}'.format(hsgtcg.count()))
