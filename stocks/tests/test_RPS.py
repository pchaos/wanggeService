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
from stocks.models import RPSprepare, RPS
from .test_RPSprepare import TestRPSprepare
import datetime

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

    @classmethod
    def setUpTestData(cls):
        # 随机插入
        Listing.importIndexListing()
        rpspreparelist = RPSprepare.importIndexListing()

    def test_getCodelist(self):
        RPS.importIndexListing()
        self.fail()



