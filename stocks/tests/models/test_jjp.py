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
from stocks.tools.jjcg import JJP, getCodeList

__author__ = 'yg'


class TestJjp(TestCase):
    def test_get_report_date_list(self):
        rd = JJP.get_report_date_list()
        self.assertTrue(len(rd) > 0, '报告日期返回为空！')
        lc = 6
        for i in range(0, lc):
            rd = JJP.get_report_date_list(listCount=i)
            if i == 0:
                self.assertTrue(len(rd) > 3, '报告日期返回为空！report_date 个数: {}'.format(len(rd)))
            else:
                self.assertTrue(len(rd) == i, '报告日期返回为空！')

    def test_get_report_date_list_atSomeDay(self):
        endDate = '2018-01-01'
        trueEndDate = '2017-12-31'
        self._check_reportdate_atsomeDay(endDate, trueEndDate)
        endDate = '2018-03-01'
        trueEndDate = '2017-12-31'
        self._check_reportdate_atsomeDay(endDate, trueEndDate)
        endDate = '2018-04-01'
        trueEndDate = '2018-03-31'
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
        code = ['000001']
        df1 = self._check_get_jjp_report(code)

        code = ['000001', '000002']
        df2 = self._check_get_jjp_report(code)
        self.assertTrue(len(df2) > len(df1), '报告周期内股票越多，数据越多：{} > {}'.format(len(df2), len(df1)))

    def test_get_jjp_report_fullcode(self):
        # 获取股票代码
        codelist = getCodeList()
        code = codelist[:10]
        df1 = self._check_get_jjp_report(code)
        print(df1[-10:])

        code = codelist[:100]
        df2 = self._check_get_jjp_report(code)
        self.assertTrue(len(df2) > len(df1), '报告周期内股票越多，数据越多：{} > {}'.format(len(df2), len(df1)))

    def _check_get_jjp_report(self, code, report_date=JJP.get_report_date_list()):
        df = JJP.get_jjp_report(code, report_date)
        self.assertTrue(len(df) > 0, '无报告')
        print('股票代码个数：{}'.format(len(df)))
        return df

    def test_filterPercent(self):
        # 获取股票代码
        codelist = getCodeList()
        code = codelist[:50]
        reportDate = JJP.get_report_date_list()
        df1 = self._check_get_jjp_report(code, reportDate)
        df = JJP.filterPercent(df1, reportDate)
        s= '结果应比原始数据少： 原始个数：{}, 过滤后数据：{}'.format(len(df1), len(df))
        self.assertTrue(len(df) < len(df1), s)
        print(s)
        self.assertTrue(len(df) > 0, '未选出数据')
        
