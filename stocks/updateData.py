# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : updateData.py.py

Description : 每天更新数据

@Author :       pchaos

date：          2018-6-20
-------------------------------------------------
Change Activity:
               2018-6-20:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
import sys; print('Python %s on %s' % (sys.version, sys.platform))
import os
sys.path.append('~/myDocs/YUNIO/tmp/gupiao/wanggeService/stocks/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wanggeService.settings")

import django; print('Django %s' % django.get_version())
# sys.path.extend([WORKING_DIR_AND_PYTHON_PATHS])
if 'setup' in dir(django): django.setup()
# import django_manage_shell; django_manage_shell.run(PROJECT_ROOT)
from stocks.models import HSGTCG, HSGTCGHold
from stocks.models import RPSprepare, RPS


def importHSGTCG():
    HSGTCGHold.importList()
    HSGTCG.importList()

def importRPS():
    # 更新最近十个交易日的RPS
    tdate = RPSprepare.getNearestTradedate(days=-10)
    RPSprepare.importStockListing(tdate)
    RPS.importStockListing(tdate)

if __name__ == '__main__':

    importHSGTCG()
    importRPS()
