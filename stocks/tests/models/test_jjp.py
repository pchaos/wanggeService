# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_jjp
   Description :
   Author :       yg
   date：          18-12-12
-------------------------------------------------
   Change Activity:
                   18-12-12:
-------------------------------------------------
"""

from unittest import TestCase

# from django.test import TestCase
from stocks.tools.jjcg import JJP

__author__ = 'yg'


class TestJjp(TestCase):
    def test_get_report_date_list(self):
        rd = JJP.get_report_date_list()
        self.assertTrue(len(rd) > 0, '报告日期返回为空！')
        lc=6
        for i in range(0,lc):
            rd = JJP.get_report_date_list(listCount=i)
            if i == 0:
                self.assertTrue(len(rd) > 3, '报告日期返回为空！report_date 个数: {}'.format(len(rd)))
            else:
                self.assertTrue(len(rd) == i, '报告日期返回为空！')

    def test_get_report_date_list_atSomeDay(self):
        endDate= '2018-01-01'
        trueEndDate='2017-12-31'
        self._check_reportdate_atsomeDay(endDate, trueEndDate)
        endDate= '2018-03-01'
        trueEndDate='2017-12-31'
        self._check_reportdate_atsomeDay(endDate, trueEndDate)
        endDate= '2018-04-01'
        trueEndDate='2018-03-31'
        self._check_reportdate_atsomeDay(endDate, trueEndDate)


    def _check_reportdate_atsomeDay(self, endDate, trueEndDate):
        rd = JJP.get_report_date_list(endDate=endDate)
        self.assertTrue(len(rd) > 0, '报告日期返回为空！')
        self.assertTrue(rd[-1] == trueEndDate, '{}报告日期返回应为：{}！'.format(endDate, trueEndDate))
        lc = 6
        for i in range(0, lc):
            rd = JJP.get_report_date_list(endDate=endDate, listCount=i)
            if i == 0:
                self.assertTrue(len(rd) > 3, '报告日期返回为空！report_date 个数: {}'.format(len(rd)))
            else:
                self.assertTrue(len(rd) == i, '报告日期返回为空！')
            self.assertTrue(rd[-1] == trueEndDate, '{}报告日期返回应为：{}！'.format(endDate, trueEndDate))

    def test_get_jjp_report(self):
        # todo error
        code = ['000001']
        self._check_get_jjp_report(code)

        # code = ['000001','000002']
        # self._check_get_jjp_report(code)

    def _check_get_jjp_report(self, code):
        df = JJP.get_jjp_report(code, JJP.get_report_date_list())
        self.assertTrue(len(df) > 0, '无')