# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_BK.py

Description :

@Author :       pchaos

tradedate：          18-5-9
-------------------------------------------------
Change Activity:
               18-5-9:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import Stockcode, BKDetail, MARKET_CHOICES, YES_NO, STOCK_CATEGORY
from stocks.models import BK
from django.utils import timezone
from datetime import datetime

__author__ = 'pchaos'


class TestBK(TestCase):
    def setUp(self):
        self.initBK()

    def initBK(self):
        """
        初始化板块顶藏；
        如果板块为空，则插入顶层板块
            bklist = [['自定义', '自定义板块'],
              ['通达信', '通达信板块'],
              ['同花顺', '同花顺板块'],
              ['其他', '其他板块'], ]
        :return:
        """
        bks = BK.objects.all()
        if bks.count() == 0:
            # 初始化板块
            bklist = [['自定义', '自定义板块'],
                      ['通达信', '通达信板块'],
                      ['同花顺', '同花顺板块'],
                      ['其他', '其他板块'], ]
            i = 0
            for b in bklist:
                bk = BK(code=str(i), name=b[0], remarks=b[1])
                bk.save()
                i += 1

    def test_TDX(self):
        """
        默认已经初始化板块名称：通达信 同花顺 自定义 其他
        """
        bkname = '通达信'
        bk = BK.objects.all().filter(name=bkname)
        self.assertTrue(bk is not None and bk[0].name == bkname, '未找到板块:{}'.format(bkname))
        bk = BK.objects.get(name=bkname)
        self.assertTrue(bk is not None and bk.name == bkname, '未找到板块:{}'.format(bkname))
        # 测试没有此板块，抛出异常
        bkname = '没有此板块'
        # self.assertRaises(TypeError, BK.objects.get(name=bkname), '未找到板块:{}'.format(bkname))
        with self.assertRaises(Exception) as context:
            bk = BK.objects.get(name=bkname)
        self.assertTrue('query does not exist.' in str(context.exception), '{}'.format(context.exception))