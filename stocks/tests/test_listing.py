# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_listing.py

Description :

@Author :       pchaos

tradedate：          18-4-12
-------------------------------------------------
Change Activity:
               18-4-12:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""

from django.test import TestCase
from stocks.models import Listing, MARKET_CHOICES, YES_NO, STOCK_CATEGORY
from stocks.models import BlockDetail, qa
from django.utils import timezone
from datetime import datetime
import pandas as pd

__author__ = 'pchaos'

import json


class TestListing(TestCase):
    def test_getCategory(self):
        c = Listing.getCategory('stock')
        self.assertTrue(c == 10, '类型不对：{}'.format(c))
        c = Listing.getCategory('index')
        self.assertTrue(c == 11, '类型不对：{}'.format(c))
        c = Listing.getCategory('etf')
        self.assertTrue(c == 12, '类型不对：{}'.format(c))
        c = Listing.getCategory('ZQ')
        self.assertTrue(c == 13, '类型不对：{}'.format(c))
        c = Listing.getCategory('NHG')
        self.assertTrue(c == 14, '类型不对：{}'.format(c))
        c = Listing.getCategory(10)
        self.assertTrue(c == 10, '类型不对：{}'.format(c))
        c = Listing.getCategory(11)
        self.assertTrue(c == 11, '类型不对：{}'.format(c))

    def test_Stockcode(self):
        a, b = MARKET_CHOICES[0]
        up_date = timezone.now()
        sc = Listing(code='tt0001', name='Test0001', timeToMarket=up_date, market=a)
        sc.save()
        # i = Listing.objects.all().count()
        i = Listing.getlist().count()
        self.assertTrue(i > 0, 'Listing count:{}'.format(i))
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

    def test_importStocklisting(self):
        """
        插入所有的A股股票代码
        :return:
        """
        oldcounts = Listing.getlist().count()
        df = Listing.importStockListing()
        print('before:{} after: {}'.format(oldcounts, Listing.getlist().count()))
        self.assertTrue(Listing.getlist().count() == oldcounts + len(df),
                        '插入未成功, after :{} before : {}; 应插入：{}条记录'.format(Listing.objects.all().count(), oldcounts,
                                                                         len(df)))
        # 再次导入，不会报错
        df = Listing.importStockListing()

    def test_importIndexlisting(self):
        oldcount = Listing.getlist('index').count()
        Listing.importIndexListing()
        count = Listing.getlist('index').count()
        self.assertTrue(count - oldcount > 500, '2018-05 指数数量应大于500， {}'.format(count - oldcount))

    def test_getCodelist(self):
        oldcounts = Listing.getlist().count()
        self.assertTrue(Listing.getlist('all').count() >= oldcounts,
                        '所有类型代码数量比股票代码数量多, after :{} before : {}; '.format(Listing.objects.all().count(), oldcounts))
        counts = 0
        for category, b in STOCK_CATEGORY:
            counts += Listing.objects.all().filter(category=category).count()
        count = Listing.getlist('all').count()
        self.assertTrue(counts == count, '明细汇总应该和总体数量一样：{} - {}'.format(counts, count))

    def test_IndexDuplocate(self):
        Listing.importIndexListing()
        indexlist = Listing.getlist('index').filter(isactived=True)
        df = pd.DataFrame(list(indexlist.values('code', 'name')))
        dup = df[df.duplicated('name')]
        for v in dup.name:
            x = None
            for d in df[df.name == v].index:
                if not x:
                    x = qa.QA_fetch_index_day_adv(df.iloc[d].code, '2018-1-1', '2018-3-1')
                else:
                    y = qa.QA_fetch_index_day_adv(df.iloc[d].code, '2018-1-1', '2018-3-1')
                    if (x.data.close[-1] == y.data.close[-1]):
                        print('重复的index: {} {}'.format(x.data.index[0][1], df.iloc[d].code))  # 重复的index
                        Listing.objects.all().filter(code=df.iloc[d].code)
                        # 更新重复代码isactived=False

                    else:
                        print('未重复的index: {}'.format(df.iloc[d].code))  # 重复的index
