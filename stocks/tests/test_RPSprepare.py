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
from stocks.models import Stockcode, STOCK_CATEGORY
from stocks.models import RPSprepare

__author__ = 'pchaos'


class TestRPSprepare(TestCase):
    def test_getCodelist(self):
        # using quantaxis
        oldcount = RPSprepare.getCodelist('index').count()
        # 测试时插入指数基础数据
        qs = Stockcode.importIndexListing()
        rps = RPSprepare(code=qs[0], rps120=1.1, rps250=1.2)
        rps.save()
        count = RPSprepare.getCodelist('index').count()
        self.assertTrue(count - oldcount > 0, '指数数量应大于0， {}'.format(count - oldcount))

    def test_importIndexListing(self):
        oldcount = RPSprepare.getCodelist('index').count()
        # 测试时插入指数基础数据
        qs = Stockcode.importIndexListing()
        RPSprepare.importIndexListing()
        count = RPSprepare.getCodelist('index').count()
        self.assertTrue(count - oldcount > 500, '2018-05 指数数量应大于500， {}'.format(count - oldcount))
