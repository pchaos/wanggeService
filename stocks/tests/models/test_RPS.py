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
from stocks.models import Stocktradedate
from stocks.models.rps import RPS, RPSprepare
from stocks.models import convertToDate
from .test_RPSprepare import TestRPSprepare
import datetime
import pandas as pd
import decimal

__author__ = 'pchaos'


class TestRPS(TestCase):

    @classmethod
    def setUpTestData(cls):
        Stocktradedate.importList()
        # Listing.importIndexListing()
        # rpspreparelist = RPSprepare.importIndexListing()

    def test_getCodelist(self):
        RPS.importIndexListing()
        self.fail()

    def test_caculateRPS(self):

        # Listing.importIndexListing()
        # rpspreparelist = RPSprepare.importIndexListing()
        qs = RPSprepare.getlist('index')
        assert qs.count() > 0, "RPSprepare.getlist('index') 返回个数应大于零"
        start, _ = Stocktradedate.get_real_date_start_end('2018-1-1', '2018-2-1')
        # qs = RPSprepare.getlist('index').filter(tradedate=convertToDate('2018-1-4'))
        qs = RPSprepare.getlist('index').filter(tradedate=start)
        df = pd.DataFrame(list(qs.values()))
        # self.assertTrue(len(df) > 0, "RPSprepare.getlist('index') 返回个数应大于零, {}".format(len(df)))
        data=RPS.caculateRPS(df)
        self.assertTrue(len(data)/len(data[data['rps120']==data['rps250']]) > 2, 'rps120等于rps250的几率很小'.format(len(data), len(data[data['rps120']==data['rps250']])) )

    def test_importStockList(self):
        Listing.importStockListing()
        filename = ''
        RPSprepare.loadModelFromFile()
        RPSprepare.importStockListing(RPSprepare.getNearestTradedate('2016-6-1'))
        qscounts = RPSprepare.getlist('stock').filter(tradedate='2018-01-04').count()
        self.assertTrue(qscounts > 2000, '当天股票数量大于2000, 实际：{}'.format(qscounts))
        RPS.importStockListing()
        qscounts = RPS.getlist('stock').filter(tradedate='2018-01-04').count()
        self.assertTrue(qscounts > 2000, '当天股票数量大于2000, 实际：{}'.format(qscounts))

    def test_RPSGTE90(self):

        tdate = RPSprepare.getNearestTradedate(days=-10)
        # rps250 选择强度大于90时，需要排除decimal.Decimal('NaN')
        counts = RPS.getlist('stock').filter(tradedate=tdate, rps250__gte=90).exclude(
                        rps250=decimal.Decimal('NaN')).count()
        print(counts)
        self.assertTrue(counts > 250, 'RPS大于90的个数应大于250，实际：{}'.format(counts) )
        self.assertTrue(counts < 400, '2018 06 21 RPS大于90的个数应小于400，实际：{}'.format(counts) )
        counts1= RPS.getlist('stock').filter(tradedate=tdate, rps250__lte=10).count()
        self.assertTrue(abs(counts - counts1) < 5, 'RPS大于90的数量应该和RPS小于10的数量差不多')

    def test_RPSGTE90bwtweendays(self):
        start='2018-6-1'; end=None
        start = RPS.getNearestTradedate(start)
        end = RPS.getNearestTradedate(end)
        qs = RPS.getlist('stock').filter(tradedate__range=(start, end), rps250__gte=90).exclude(
            rps250=decimal.Decimal('NaN')).values('code').distinct()
        count1 = qs.values('code').distinct()
        qs =  RPS.getlist('stock').filter(tradedate__range=(start, end), code__in=qs.values('code')).exclude(
            rps250=decimal.Decimal('NaN'))
        count2 = qs.values('code').distinct()
        self.assertTrue(count1 == count2, '股票数量应该相同 {} == {}'.format(count1, count2))