from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import numpy as np
import time, datetime
import QUANTAXIS as QA
from pandas import pandas as pd, concat
import datetime
import os


def getCodeList():
    QA.QA_util_log_info('股票列表')
    data = QA.QAFetch.QATdx.QA_fetch_get_stock_list('stock')
    # 获取股票代码
    return [i[0] for i in data.index]


DATE_FORMAT = '%Y-%m-%d'


def convertToDate(date, dateformat=DATE_FORMAT):
    """ 转换为日期类型
path
    :param date: DATE_FORMAT = '%Y-%m-%d'
    例如： '2017-01-01'

    :return:  返回日期 date.date()
    """
    try:
        date = datetime.datetime.strptime(date, dateformat)
        return date.date()
    except TypeError:
        return date


class JJP():
    '''
    基金占流通股比更新例
    '''

    def __init__(self, cvspath=''):
        if len(cvspath) == 0:
            self.cvspath = '/tmp/'
        else:
            self.cvspath = cvspath

    @staticmethod
    def get_jjp_report(code, report_date=[]):
        '''
            获取基金持股占比

        :param code: 单个股票或股票列表
        :param report_date: list of date;
            example:
            ['2018-03-31', '2018-06-30', '2018-09-30']

        :return:
        '''
        # res=QA.QA_fetch_financial_report(['000002','000026','000415','000417','600100'],['2017-12-31','2018-03-31','2018-06-30','2018-09-30'])
        res = QA.QA_fetch_financial_report(code, report_date)
        # 基金占比
        myres = res['fundsShareholding'] / res['listedAShares']
        df = pd.DataFrame(myres)
        df.columns = ['percent']
        df = df.reset_index()
        #
        myres = res['socialSecurityShareholding'] / res['listedAShares']
        df1 = pd.DataFrame(myres)
        df1.columns = ['ssspercent']
        df1 = df1.reset_index()
        del df1['report_date']
        del df1['code']
        return concat([df, df1], axis=1)

    @staticmethod
    def get_report_date_list(endDate='{}'.format(datetime.datetime.now().strftime('%Y-%m-%d')), listCount=3):
        ''' 返回endDate日期前的交易日期

        :param endDate: 查询截止日期；默认为当前日期
        :param listCount:  返回报告日期列表个数；listCount = 0 时，返回上一年到目前报告日期列表
        :return: 返回值例子： ['2018-03-31', '2018-06-30', '2018-09-30']
        '''
        baselist = ['03-31', '06-30', '09-30', '12-31']
        endDate = convertToDate(endDate)
        lastYear = endDate.year
        firstYear = lastYear - listCount // 4 - 1
        alist = []
        for i in range(firstYear, lastYear):
            # 不包含endDate 所在当年的日期
            for j in range(len(baselist)):
                alist.append('{}-{}'.format(i, baselist[j]))
        for j in range(len(baselist)):
            if endDate.month > int(baselist[j][:2]):
                alist.append('{}-{}'.format(lastYear, baselist[j]))
        return alist[-listCount:]

    @staticmethod
    def filterPercent(df, report_date=[], percent=0.03):
        '''
        获取基金持股占比大于percent的代码列表
        :param df:
        :param report_date:
        :param percent:
        :return:
        '''
        alist = []
        for rd in report_date[::-1]:
            # 报告日期反序
            if rd == report_date[-1]:
                # 第一次判断
                tdf = JJP._filterPercent(df, report_date, percent)
            else:
                pass
            if len(tdf)> 0:
                alist.append(tdf)
        return JJP._df2code(alist)

    @staticmethod
    def _df2code(alist):
        '''
        将代码去重
        :param alist:
        :return:
        '''
        aset = set()
        for df in alist:
            aset = aset | set(df.code)
        return list(aset)

    @staticmethod
    def _filterPercent(df, report_date, percent):
        # df = df[((df['percent'] > percent) | ((df['percent'] < percent) & (df['percent'] + df['ssspercent'] >= percent)))]
        return df[df['percent'] + df['ssspercent'] >= percent]

# today = '{}'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
# jjp= JJP()
# df = jjp.get_jjp_report(codelist, jjp.get_report_date_list())
# # myres= res['fundsShareholding']/ res['totalCapital']
#
# # 基金占比小于3%，基金+社保持股占比大于3%
# df[(df['percent'] < 0.03) & (df['percent'] + df['ssspercent'] >= 0.03)]
# df[df['percent'] >= 0.03].append(df[(df['percent'] < 0.03) & (df['percent'] + df['ssspercent'] >= 0.03)])
# df[((df['percent'] > 0.03) | ((df['percent'] < 0.03) & (df['percent'] + df['ssspercent'] >= 0.03)))]
#
# # 最后周期
# lastperoid = '2018-09-30'
# preperoid = '2018-06-30'
# jjp = df[((df['report_date'] == lastperoid) & (df['percent'] > 0.03))]
# # 最后周期数据未出,查询上个周期
# df1 = df[(((df['report_date'] == lastperoid) & (df['percent'] == 0.0)))]
# df2 = df[((df['report_date'] == preperoid) & (df['percent'] > 0.03))]
# st1 = set(df1.code)
# st2 = set(df2.code)
# # 最后周期数据未出，上个周期基金持股大于等于3%的股票代码
# precodelist = list(st1 & st2)
#
# l = list(set(jjp.code) | set(precodelist))
