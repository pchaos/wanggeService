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
import time, datetime
import random

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

def MAUpper( n):
    import QUANTAXIS as qa
    tdate = HSGTCG.getNearestTradedate()
    tdate = HSGTCG.getNearestTradedate(tdate, -(n + 100))
    # hsg = HSGTCG.getlist().filter(tradedate__gte=(tdate, tdate), hamount__gte=8000)
    hsg = HSGTCG.getlist().filter(tradedate__gte=tdate).order_by('code', 'tradedate')
    df = pd.DataFrame(list(hsg.values('hamount', 'code', 'tradedate')))
    results = []
    for c in df.code.unique():
        v = df[df['code'] == c]
        ma1 = qa.MA(v.hamount, n)
        if (ma1.iloc[-1] - ma1.iloc[-2]) >= 0:
            results.append(v.code.iloc[0])
            continue
    return results


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
            for x in ['lxml', 'xml', 'html5lib']:
                # 可能会出现lxml版本大于4.1.1时，获取不到table
                try:
                    time.sleep(random.random() / 4)
                    soup = BeautifulSoup(browser.page_source, x)
                    table = soup.find_all(id='tb_cgtj')[0]
                    if table:
                        break
                except:
                    time.sleep(0.1)
                    print('using BeautifulSoup {}'.format(x))
            # soup = BeautifulSoup(browser.page_source, 'lxml')
            # table = soup.find_all(id='tb_cgtj')[0]
            df = pd.read_html(str(table), header=1)[0]
            df.columns = ['date', 'related', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday', 'fiveday',
                          'tenday']
            for i in df.index:
                v = df.iloc[i]
                print('{} {} {} {}'.format(v.close, v.hvol, v.hamount, v.hpercent))
                HSGTCG.objects.get_or_create(code=code, close=v.close, hvol=str2Float(v.hvol),
                                             hamount=str2Float(v.hamount), hpercent=v.hpercent,
                                             tradedate=convertToDate(v.date))
        finally:
            if browser:
                browser.close()
        hsgtcg = HSGTCG.getlist(code)
        # hsgtcg = HSGTCG.getlist()
        print(hsgtcg)
        self.assertTrue(hsgtcg.count() > 10, '保存的数量： {}'.format(hsgtcg.count()))
        self.assertTrue(isinstance(hsgtcg[0].tradedate, datetime.date))
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

    def test_deleteNotTradedate(self):
        # 删除不是交易日的数据
        for d in set(list(HSGTCG.objects.all().values_list('tradedate'))):
            if not Stocktradedate.if_tradeday(d[0]):
                HSGTCG.objects.all().filter(tradedate=d[0]).delete()
                print(d[0])

    def test_newcomingin(self):
        """ 最近n个交易日，新进市值大于8000万的个股

        :return:
        """
        n = 5
        tdate = HSGTCG.getNearestTradedate()
        tdate1 = HSGTCG.getNearestTradedate(tdate, -n)
        tdate2 = HSGTCG.getNearestTradedate(tdate1, -n - 1)
        yesterdayhsg = HSGTCG.getlist().filter(tradedate=tdate2, hamount__gte=8000, )
        hsg = HSGTCG.getlist().filter(tradedate__range=(tdate1, tdate), hamount__gte=8000)
        newcomming = hsg.exclude(code__in=yesterdayhsg.values_list('code')).values('code')
        print(newcomming)


    def test_hamountMA(self):

        # n日持仓增加
        n = 5
        malist1 = MAUpper(n)
        n=10
        malist2 = MAUpper(n)
        HSGTCG.dfNotInAnotherdf(pd.DataFrame(malist1), pd.DataFrame(malist2))
        up = list(HSGTCG.dfNotInAnotherdf(pd.DataFrame(malist1), pd.DataFrame(malist2))[0])

