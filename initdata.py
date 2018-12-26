# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     initdata.py
   Description : 初始化数据库基础数据
   Author :       pchaos
   date：          18-12-26
-------------------------------------------------
   Change Activity:
                   18-12-26:
-------------------------------------------------
"""
__author__ = 'pchaos'

import sys; print('Python %s on %s' % (sys.version, sys.platform))
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wanggeService.settings")

import django; print('Django %s' % django.get_version())
if 'setup' in dir(django): django.setup()

import pandas as pd
import numpy as np
from stocks.models import *
import QUANTAXIS as qa
import datetime

from stocks.models import Stocktradedate
# 交易日期
qs = Stocktradedate.getlist()
if qs.count() > 0:
    qs.delete()
qs = Stocktradedate.importList()
print('交易日期：{}'.format(qs.count()))

#基础数据
from stocks.models import Listing
qs = Listing.getlist()
if qs.count() > 0:
    qs.delete()
qs = Listing.importStockListing()
print('导入股票：{}'.format(qs.count()))
qs = Listing.getlist('index')
if qs.count() > 0:
    qs.delete()
qs = Listing.importIndexListing()
print('导入指数：{}'.format(qs.count()))

