# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : updateStockData.py.py

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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wanggeService.settings")

import django; print('Django %s' % django.get_version())
# sys.path.extend([WORKING_DIR_AND_PYTHON_PATHS])
if 'setup' in dir(django): django.setup()
# import django_manage_shell; django_manage_shell.run(PROJECT_ROOT)
from stocks.models import HSGTCG, HSGTCGHold
from stocks.models import RPSprepare, RPS
from stocks.models import FreshHigh

import datetime
from QUANTAXIS import (QA_SU_save_etf_day, QA_SU_save_index_day, QA_SU_save_stock_min,
                       QA_SU_save_stock_block, QA_SU_save_stock_day,QA_SU_save_etf_min,
                       QA_SU_save_stock_list, QA_SU_save_stock_xdxr,
                       QA_util_log_info)

def saveTDXday():
    print('SAVE/UPDATE {}'.format(datetime.datetime.now()))
    QA_SU_save_stock_day('tdx')
    QA_SU_save_stock_xdxr('tdx')
    # QA_SU_save_etf_day('tdx')
    # QA_SU_save_index_day('tdx')
    QA_SU_save_stock_list('tdx')
    QA_SU_save_stock_block('tdx')


def importHSGTCG():
    HSGTCGHold.importList()
    HSGTCG.importList()

def importRPS():
    # 更新最近十个交易日的RPS
    tdate = RPSprepare.getNearestTradedate(days=-10)
    RPSprepare.importStockListing(tdate)
    RPS.importStockListing(tdate)

def importFreshHigh():
    tdate = RPSprepare.getNearestTradedate(days=-10)
    FreshHigh.importList(tdate, n=(datetime.datetime.now().date() - tdate).days)

def importALl():
    if (0 == datetime.datetime.now().weekday() or datetime.datetime.now().weekday()
> 4) or datetime.datetime.now().time().hour * 100 + datetime.datetime.now().time().minute > 1730:
        # 每天17:30点有后才更新数据
        saveTDXday()
        importRPS()
        importFreshHigh()
    else:
        print('时间未到：{}'.format(datetime.datetime.now()))

if __name__ == '__main__':

    importHSGTCG()
    importALl()
else:
    importALl()
