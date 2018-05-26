# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_RPS.py

Description :

@Author :       pchaos

date：          18-5-18
-------------------------------------------------
Change Activity:
               18-5-18:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import Listing, STOCK_CATEGORY
from stocks.models import RPSprepare, RPS, stocktradedate
from stocks.models import convertToDate
from .test_RPSprepare import TestRPSprepare
import datetime
import pandas as pd

__author__ = 'pchaos'


class TestRPS(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     super(TestRPS, cls).setUpClass()
    #     cls.qslist = Listing.importIndexListing()
    #     cls.listing = Listing.getlist('index')
    #
    # @classmethod
    # def tearDownClass(cls):
    #     cls.qslist = None
    #     cls.listing = None

    # @classmethod
    # def setUpTestData(cls):
    #     # 随机插入
    #     Listing.importIndexListing()
    #     rpspreparelist = RPSprepare.importIndexListing()

    def test_getCodelist(self):
        RPS.importIndexListing()
        self.fail()

    def test_caculateRPS(self):
        stocktradedate.importList()
        Listing.importIndexListing()
        rpspreparelist = RPSprepare.importIndexListing()
        qs = RPSprepare.getlist('index')
        assert qs.count() > 0, "RPSprepare.getlist('index') 返回个数应大于零"
        start, _ = stocktradedate.get_real_datelist('2018-1-1', '2018-2-1')
        # qs = RPSprepare.getlist('index').filter(tradedate=convertToDate('2018-1-4'))
        qs = RPSprepare.getlist('index').filter(tradedate=start)
        df = pd.DataFrame(list(qs.values()))
        # self.assertTrue(len(df) > 0, "RPSprepare.getlist('index') 返回个数应大于零, {}".format(len(df)))
        data=RPS.caculateRPS(df)
        self.assertTrue(len(data)/len(data[data['rps120']==data['rps250']]) > 2, 'rps120等于rps250的几率很小'.format(len(data), len(data[data['rps120']==data['rps250']])) )



