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
import random

__author__ = 'pchaos'


class TestRPSprepare(TestCase):
    def test_getCodelist(self):
        # using quantaxis
        oldcount = RPSprepare.getlist('index').count()
        # 测试时插入指数基础数据
        qs = Listing.importIndexListing()
        rps = self.insertRandomRPSprepare(qs[0])
        d = rps[0].tradedate
        count = RPSprepare.getlist('index').count()
        self.assertTrue(count - oldcount > 0, '指数数量应大于0， {}'.format(count - oldcount))
        print('数据库中有{}记录。'.format(count))
        qsrps = RPSprepare.getlist('index')
        self.assertTrue(qsrps[0].tradedate == d, '日期保存失败：{} {}'.format(qsrps[0].tradedate, d))
        qsrps.delete()

        # 测试tradedate保存
        d = (datetime.datetime.now() - datetime.timedelta(300)).date()
        querysetlist = []
        n = 10
        for i in range(n):
            rps = RPSprepare(code=qs[1], rps120=i + 1, rps250=1.2, tradedate=d + datetime.timedelta(i + 1))
            querysetlist.append(rps)
        RPSprepare.objects.bulk_create(querysetlist)
        qsrps = RPSprepare.getlist('index')
        for i in range(1, n, 1):
            self.assertTrue(qsrps[i].tradedate == d + datetime.timedelta(i + 1),
                            '数据库中{} ！= {}'.format(qsrps[i].tradedate, d + datetime.timedelta(i + 1)))
            self.assertTrue(qsrps[i].rps120 == 1 + i,
                            '数据库中{} ！= {}'.format(qsrps[i].rps120, i + 1))
    @classmethod
    def insertRandomRPSprepare(cls, listing=None, insertCount=1):
        """ 随机插入insertCount个RPSprepare
            listing为RPSprepare的外键，默认为空时，自动获取listing

        :param listing: 对应RPSprepare的外键
        :param insertCount: 自动插入的个数
        :return: 插入成功的RPSprepare list
        """
        if listing is None:
            qslist = Listing.importIndexListing()
            listing = qslist[random.randint(0, len(qslist) - 1)]
        rpslist = []
        beforday = insertCount * 2 + 1
        d = (datetime.datetime.now() - datetime.timedelta(random.randint(1, beforday))).date()
        for i in range(insertCount):
            rps = RPSprepare(code=listing, rps120=1.1, rps250=1.2, tradedate=d)
            rps.save()
            rpslist.append(rps)
            assert d == rps.tradedate, '保存前后tradedate： {} : {}'.format(d, rps.tradedate)
            d = d + datetime.timedelta(1)
        return rpslist

        def test_importIndexListing(self):
            oldcount = RPSprepare.getlist('index').count()
            # 测试时插入指数基础数据
            qs = Listing.importIndexListing()
            RPSprepare.importIndexListing()
            count = RPSprepare.getlist('index').count()
            self.assertTrue(count - oldcount > 500, '2018-05 指数数量应大于500， {}'.format(count - oldcount))
            print(RPSprepare.getlist('index')[0])
