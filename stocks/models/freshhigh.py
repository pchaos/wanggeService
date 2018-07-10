# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : freshhigh.py

Description :

@Author :       pchaos

date：          18-7-9
-------------------------------------------------
Change Activity:
               18-7-9:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.db import models
from django.db import transaction
from stocks.models import StockBase
from stocks.models import Listing

class FreshHigh(StockBase):
    code = models.ForeignKey(Listing, verbose_name='代码', max_length=10, db_index=True, null=True)
    high = models.DecimalField(verbose_name='价格', max_digits=9, decimal_places=3, null=True)
    low = models.DecimalField(verbose_name='价格', max_digits=9, decimal_places=3, null=True)
    htradedate = models.DateField(verbose_name='最高点日期', null=True, db_index=True)
    ltradedate = models.DateField(verbose_name='最低点日期', null=True, db_index=True)

    class Meta:
        abstract = True

