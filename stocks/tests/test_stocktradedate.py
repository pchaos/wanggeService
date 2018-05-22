# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_stocktradedate.py

Description :

@Author :       pchaos

date：          18-5-21
-------------------------------------------------
Change Activity:
               18-5-21:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
import datetime
from stocks.models import stocktradedate

__author__ = 'pchaos'


class TestStocktradedate(TestCase):

    def test_importList(self):
        qs = stocktradedate.importList()
        day = datetime.datetime.strptime('1991-12-31', '%Y-%m-%d')
        self.assertTrue(qs.filter(tradedate__lte=day).count() == 264,
                        '1991年之前的交易日共：{}'.format(qs.filter(tradedate__lte=day).count()))

        day = datetime.datetime.strptime('2017-12-31', '%Y-%m-%d')
        self.assertTrue(qs.filter(tradedate__lte=day).count() == 6613,
                        '2018年之前的交易日共：{}'.format(qs.filter(tradedate__lte=day).count()))

        day = datetime.datetime.strptime('2018-3-31', '%Y-%m-%d')
        self.assertTrue(qs.filter(tradedate__lte=day).count() > 6613,
                        '2018年之前的交易日共：{}'.format(qs.filter(tradedate__lte=day).count()))

    def test_trade_date_sse(self):
        qs = stocktradedate.importList()
        day = datetime.datetime.now()
        sd = stocktradedate()
        self.assertTrue(qs.filter(tradedate__lte=day).count() == sd.trade_date_sse.count(),
                        '2018年之前的交易日共：{}'.format(qs.filter(tradedate__lte=day).count()))

    def test_if_trade(self):
        qs = stocktradedate.importList()
        day = datetime.datetime.strptime('2018-5-21', '%Y-%m-%d')
        self.assertTrue(stocktradedate.if_trade(day), '{} 是交易日'.format(day))

    def test_get_real_date(self):
        qs = stocktradedate.importList()
        date= '2018-5-21'
        day = datetime.datetime.strptime(date, '%Y-%m-%d')
        self.assertTrue(stocktradedate.get_real_date(day) == day, '({}) != ({})'.format(stocktradedate.get_real_date(day), day))

        date= '2018-5-20'
        day = datetime.datetime.strptime(date, '%Y-%m-%d')
        self.assertFalse(stocktradedate.get_real_date(day) == day, '({}) != ({})'.format(stocktradedate.get_real_date(day), day))