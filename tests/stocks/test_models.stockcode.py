# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_models.stockcode.py

Description :

@Author :       pchaos

date：          18-4-12
-------------------------------------------------
Change Activity:
               18-4-12:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""

from django.test import TestCase as TC
# from unittest import TestCase

__author__ = 'pchaos'

from stocks.models import Stockcode as SC, ZXG, MARKET_CHOICES, YES_NO

class TestStockcode(TC):
    def setup(self):
        print("======in setUp")

    def tearDown(self):
        print("======in tearDown")

    def test_Stockcode(self):
        sc = SC(code='tt0001', name='Test0001', market=MARKET_CHOICES[0])
        sc.save()
        i= sc.objects.all().count()
        self.assertTrue(i > 0, 'Stockcode count:{}'.format(i))

if __name__ == '__main__':
    TC.run()