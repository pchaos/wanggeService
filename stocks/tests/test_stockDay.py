# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_stockDay.py

Description :

@Author :       pchaos

tradedate：          18-5-11
-------------------------------------------------
Change Activity:
               18-5-11:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import Listing, BKDetail, MARKET_CHOICES, YES_NO, STOCK_CATEGORY
from stocks.models import StockDay
from django.utils import timezone
from datetime import datetime

__author__ = 'pchaos'


class TestStockDay(TestCase):
    def test_saveStockDay(self):
        a, _ = MARKET_CHOICES[0]
        code = 'tt0001'
        up_date = datetime.now()
        sc = Listing(code=code, name='Test0001', timeToMarket=up_date, market=a)
        sc.save()
        sdlist = StockDay.objects.all().count() # 此处不能为StockDay.objects.all()，否则由于lazy算法，并不会马上获取数据，导致更新数据后才查询数据
        code = Listing.objects.get(code=code)
        sd = StockDay(code=code, open=1, close=2, high=3, low=0, volumn=100000, amount=230000, date=datetime.now())
        sd.save()
        print(sdlist, code, sd)
        self.assertTrue(StockDay.objects.all().count() > sdlist, '未保存成功, {} > {}：{}'.format(StockDay.objects.all().count(), sdlist, sd.__dict__))
