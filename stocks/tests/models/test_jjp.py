# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_jjp
   Description :
   Author :       pchaos
   date：          18-12-12
-------------------------------------------------
   Change Activity:
                   18-12-12:
-------------------------------------------------
"""

from unittest import TestCase
import unittest
from stocks.tools.jjcg import JJP, getCodeList

__author__ = 'pchaos'


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
        endDate = 'http://blog.sina.com.cn/s/articlelist_1256938773_3_1.html2018-01-01'
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
        codes = codelist[:50]
        fcodes = self._filterPercent(codes)
        print('股票总数：{}, 占比%：{:5.2f}\n返回过滤后的代码：{}'.format(len(codes), len(fcodes)/len(codes)*100, fcodes))
        reportDate = JJP.get_report_date_list()[-1]
        print(self._check_get_jjp_report(fcodes, reportDate))

        codes = codelist[:500]
        self._filterPercent(codes)

        codes = codelist
        fcodes = self._filterPercent(codes)
        fcodes2 = self._filterPercent(codes, percent=0.045)
        self.assertTrue(len(fcodes2) < len(fcodes), '过滤条件percent大的，返回值应该小')

    def _filterPercent(self, code, percent=0.03):
        reportDate = JJP.get_report_date_list()
        df1 = self._check_get_jjp_report(code, reportDate)
        filterCodes = JJP.filterPercent(df1, reportDate, percent=percent)
        s = '结果应比原始数据少： 原始个数：{}, 过滤后数据：{}'.format(len(df1), len(filterCodes))
        self.assertTrue(len(filterCodes) < len(df1), s)
        print(s)
        self.assertTrue(len(filterCodes) > 0, '未选出数据')
        return filterCodes

    def test_filterPercent2File(self):
        # 基金占比大于3%
        # 保存文件到临时目录
        # fname= '/dev/shm/temp/jjp{}.EBK'.format('20181214')
        fname= '/dev/shm/temp/jjp{}.EBK'.format('20181221')
        # 获取股票代码
        codelist = getCodeList()
        codes = codelist
        fcodes = self._filterPercent(codes, percent=0.03)
        with open(fname, 'w') as f:
            for item in fcodes:
                f.write("{}\n".format('1{}'.format(item) if item[0] == '6' else '0{}'.format(item)))


if __name__ == "__main__":
    unittest.main()
