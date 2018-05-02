# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_strategy.py

Description :

@Author :       pchaos

date：          18-5-2
-------------------------------------------------
Change Activity:
               18-5-2:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from strategies.models import Strategy, StrategyType
from stocks.models import Stockcode

__author__ = 'pchaos'


class TestStrategy(TestCase):
    def test_baseStrategy(self):
        code = 'test01'
        testname = 'testStrategyType 01'
        testremark = 'test remarks'
        strategytype = StrategyType(code=code, name=testname, remark=testremark)
        strategytype.save()
        sell_choice = 0
        stcode = 'Strategy 01'
        stname = 'Strategy name 01'
