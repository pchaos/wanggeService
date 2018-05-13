# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_listing.py

Description :

@Author :       pchaos

date：          18-4-12
-------------------------------------------------
Change Activity:
               18-4-12:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""

from django.test import TestCase
from stocks.models import Stockcode, BKDetail, MARKET_CHOICES, YES_NO, STOCK_CATEGORY
from django.utils import timezone
from datetime import datetime

__author__ = 'pchaos'

import json


class TestListing(TestCase):
    def test_Stockcode(self):
        a, b = MARKET_CHOICES[0]
        up_date = timezone.now()
        sc = Stockcode(code='tt0001', name='Test0001', timeToMarket=up_date, market=a)
        sc.save()
        i = Stockcode.objects.all().count()
        self.assertTrue(i > 0, 'Stockcode count:{}'.format(i))
        # object to json
        print('sc.__dict__ : {}'.format(sc.__dict__))
        print('json sc.__dict__ : {}'.format(json.dumps(sc, default=str)))
        # from bson import json_util
        # print('bson sc.__dict__ : {}'.format(json.dumps(sc, default=json_util.default)))

    def test_importStockcode(self):
        """
        测试导入股票代码
        :return:
        """
        from oneilquant.ONEIL.Oneil import OneilKDZD as oneil
        oq = oneil()
        n1 = 365
        df = oq.listingDate(n1)
        len1 = len(df)
        self.assertTrue(len(df) > 2500, "上市一年以上股票数量，2018年最少大于2500只")
        print(df[:10]['timeToMarket'], df['name'])
        print(df.index[:10])

    def test_importAllisting(self):
        """
        插入所有的A股股票代码
        :return:
        """
        oldcounts = Stockcode.objects.all().count()
        df = Stockcode.importAllListing()
        print(Stockcode.objects.all().count())
        self.assertTrue(Stockcode.objects.all().count() == oldcounts + len(df),
                        '插入未成功, after :{} before : {}; 应插入：{}条记录'.format(Stockcode.objects.all().count(), oldcounts,
                                                                         len(df)))
