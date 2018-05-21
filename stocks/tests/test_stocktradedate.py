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
        year = datetime.datetime.strptime('1991-12-31', '%Y-%m-%d')
        self.assertTrue(qs.filter(tradedate__lte=year).count() == 264, '1991年之前的交易日共：{}'.format(qs.filter(tradedate__lte=year).count()))

        year = datetime.datetime.strptime('2017-12-31', '%Y-%m-%d')
        self.assertTrue(qs.filter(tradedate__lte=year).count() == 6613,
                        '2018年之前的交易日共：{}'.format(qs.filter(tradedate__lte=year).count()))

        year = datetime.datetime.strptime('2018-3-31', '%Y-%m-%d')
        self.assertTrue(qs.filter(tradedate__lte=year).count() > 6613,
                        '2018年之前的交易日共：{}'.format(qs.filter(tradedate__lte=year).count()))
