# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_RPSprepare.py

Description :

@Author :       pchaos

tradedate：          18-5-16
-------------------------------------------------
Change Activity:
               18-5-16:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import Listing, STOCK_CATEGORY
from stocks.models import RPSprepare
import datetime

__author__ = 'pchaos'


class TestRPSprepare(TestCase):
    def test_getCodelist(self):
        # using quantaxis
        oldcount = RPSprepare.getCodelist('index').count()
        # 测试时插入指数基础数据
        qs = Listing.importIndexListing()
        d = (datetime.datetime.now() - datetime.timedelta(300)).date()
        rps = RPSprepare(code=qs[0], rps120=1.1, rps250=1.2, tradedate=d)
        rps.save()
        count = RPSprepare.getCodelist('index').count()
        self.assertTrue(count - oldcount > 0, '指数数量应大于0， {}'.format(count - oldcount))
        print('数据库中有{}记录。'.format(count))
        qsrps = RPSprepare.getCodelist('index')
        self.assertTrue(qsrps[0].tradedate == d, '日期保存失败：{} {}'.format(qsrps[0].tradedate, d))
        qsrps.delete()

        # 测试tradedate保存
        d = (datetime.datetime.now() - datetime.timedelta(300)).date()
        querysetlist = []
        n = 10
        for i in range(n):
            rps = RPSprepare(code=qs[1], rps120=1 + i, rps250=1.2, tradedate=d + datetime.timedelta(i + 1))
            querysetlist.append(rps)
        RPSprepare.objects.bulk_create(querysetlist)
        qsrps = RPSprepare.getCodelist('index')
        for i in range(1, n, 1):
            self.assertTrue(qsrps[i].tradedate == d + datetime.timedelta(i + 1),
                            '数据库中{} ！= {}'.format(qsrps[i].tradedate, d + datetime.timedelta(i + 1)))
            self.assertTrue(qsrps[i].rps120 == 1 + i,
                            '数据库中{} ！= {}'.format(qsrps[i].rps120, i + 1))

    def test_importIndexListing(self):
        oldcount = RPSprepare.getCodelist('index').count()
        # 测试时插入指数基础数据
        qs = Listing.importIndexListing()
        RPSprepare.importIndexListing()
        count = RPSprepare.getCodelist('index').count()
        self.assertTrue(count - oldcount > 500, '2018-05 指数数量应大于500， {}'.format(count - oldcount))
        print(RPSprepare.getCodelist('index')[0])
