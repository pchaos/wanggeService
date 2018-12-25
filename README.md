# wanggeService
网格交易计算服务（django）

* 进入wanggeService目录
* 初始化数据库

python manage.py makemigrations

python manage.py migrate

* 创建超级用户

python manage.py createsuperuser

* 启动django服务

python manage.py runserver


* 第一次初始化数据后才能用updateData.sh更新数据

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

** 交易日期

from stocks.models import Stocktradedate
qs = Stocktradedate.getlist()
if qs.count() > 0:
    qs.delete()
qs = Stocktradedate.importList()
print('交易日期：{}'.format(qs.count()))

**基础数据

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

