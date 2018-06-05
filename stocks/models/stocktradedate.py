# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : stocktradedate.py

Description :

@Author :       pchaos

date：          2018-5-29
-------------------------------------------------
Change Activity:
               18-5-29:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
import datetime

import QUANTAXIS as qa
import pandas as pd
from django.db import models

from stocks.models import convertToDate

__author__ = 'pchaos'


class Stocktradedate(models.Model):
    tradedate = models.DateField(verbose_name='交易日期', unique=True)

    @classmethod
    def getlist(cls, start=None, end=None):
        """

        """
        # 返回所有代码
        if start is None and end is None:
            return cls.objects.all()
        else:
            if start is None:
                start = datetime.datetime(1990, 1, 1)
            if end is None:
                end = datetime.datetime.now().date()
            return cls.objects.all().filter(tradedate__gte=start, tradedate__lte=end)

    @classmethod
    def importList(cls):
        """
        从qa.QAUtil.QADate_trade.trade_date_sse导入交易日期
        :return: 返回 .objects.all()
        """
        data = qa.QAUtil.QADate_trade.trade_date_sse
        if len(data) > cls.getlist().count():
            querysetlist = []
            for v in [d.date() for d in pd.to_datetime(data)]:
                querysetlist.append(Stocktradedate(tradedate=v))
            cls.objects.bulk_create(querysetlist)
        return cls.getlist()

    def __str__(self):
        return '{}'.format(self.tradedate.strftime('%Y-%m-%d'))

    @classmethod
    def getlist(cls):
        """

        """
        # 返回所有代码
        return cls.objects.all()

    @classmethod
    def get_real_date(cls, date, towards=-1):
        """
        获取真实的交易日期,其中,第三个参数towards是表示向前/向后推
        towards=1 日期向后迭代
        towards=-1 日期向前迭代
        @ yutiansut

        """
        while not cls.if_tradeday(date):
            date = str(datetime.datetime.strptime(
                str(date)[0:10], '%Y-%m-%d') + datetime.timedelta(days=towards))[0:10]
        else:
            return datetime.datetime.strptime(str(date)[0:10], '%Y-%m-%d')

    @property
    def trade_date_sse(self):
        try:
            return self.tradedatelist
        except Exception as e:
            self.tradedatelist = Stocktradedate.getlist().filter(tradedate__lte=datetime.datetime.now().date()).values()
            # Stocktradedate.objects.values_list('tradedate').filter(tradedate__lte=datetime.datetime.now().date())
            return self.tradedatelist

    @trade_date_sse.setter
    def trade_date_sse(self, value):
        pass

    @classmethod
    def if_tradeday(cls, day):
        '日期是否交易'
        try:
            _sd = Stocktradedate()
            _sd.trade_date_sse.get(tradedate=(str(day)[:10]))
            _sd = None
            return True
        except Exception as e:
            return False

    @classmethod
    def nextTradeday(cls, tradeday=None, n=1):
        """ 下一交易日

        :param tradeday:
        :param n:
        :return:
        """
        return cls.date_gap(tradeday, n, 'gt')

    @classmethod
    def preTradeday(cls, tradeday=None, n=1):
        return cls.date_gap(tradeday, n, 'lt')

    @classmethod
    def date_gap(cls, date, gap, methods):
        """[summary]

        Arguments:
            date {[type]} -- [description]
            gap {[type]} -- [description]
            methods {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        try:
            datesse = cls()
            dateid = datesse.trade_date_sse.filter(tradedate=date)[0]['id']
            if methods in ['>', 'gt']:
                td = datesse.trade_date_sse.filter(id=dateid + gap)
                return td[0]['tradedate']
            elif methods in ['>=', 'gte']:
                td = datesse.trade_date_sse.filter(id=dateid + gap - 1)
                return td[0]['tradedate']
            elif methods in ['<', 'lt']:
                td = datesse.trade_date_sse.filter(id=dateid - gap)
                return td[0]['tradedate']
            elif methods in ['<=', 'lte']:
                td = datesse.trade_date_sse.filter(id=dateid - gap + 1)
                return td[0]['tradedate']
            elif methods in ['==', '=', 'eq']:
                return date

        except:
            return 'wrong date'

    @classmethod
    def get_real_date_start_end(cls, start, end):
        """
        取数据的真实区间,返回的时候用 start,end=Stocktradedate.get_rev2ray v2ctl verifyal_datelist()
        @yutiansut
        2017/8/10

        当start end中间没有交易日 返回None, None
        @yutiansut/ 2017-12-19
        """
        alist = cls.get_real_datelisting(start, end)
        if alist.count() == 0:
            return None, None
        else:
            # (start_tradedate, end_tradedate)
            return (alist[0]['tradedate'], alist[len(alist) - 1]['tradedate'])

    @classmethod
    def get_real_datelisting(cls, start, end):
        """ 取数据的真实区间列表

        :param start:
        :param end:
        :return: list of datetime.date()
        """

        datesse = cls()
        return datesse.trade_date_sse.filter(tradedate__gte=convertToDate(start), tradedate__lte=convertToDate(end))

    class Meta:
        # app_label ='rps计算'
        verbose_name = 'A股交易日'