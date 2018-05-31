# -*- coding: utf-8 -*-

"""
-------------------------------------------------

@File    : hsgtcg.py

Description : 沪深港通持股

@Author :       pchaos

date：          2018-5-30
-------------------------------------------------
Change Activity:
               2018-5-30:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
MINHAMOUNT = 7000  # 最小关注的北向持仓金额

from django.db import models
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time


class HSGTCGBase(models.Model):
    @staticmethod
    def hz2Num(astr):
        """ 统一以"万"为单位

        :param astr: 带有“亿”、“万”等的字符串
        :return: 以"万"为单位的浮点数
        """
        try:
            if type(astr) is str:
                y = '亿'
                if astr.find(y) >= 0:
                    return str(np.round(float(astr.replace(y, '')) * 100000, 2))
                y = '万'
                if astr.find(y) >= 0:
                    return str(np.round(float(astr.replace(y, '')), 2))
                else:
                    return str(np.round(float(astr) / 10000, 2))
        except:
            return '0'

    @staticmethod
    def getBrowser():

        opts = Options()
        opts.set_headless()
        assert opts.headless  # operating in headless mode
        browser = webdriver.Firefox()
        browser.maximize_window()
        return browser

    @staticmethod
    def scrap(url, browser):
        """ 抓取网页内容，子类需要实现该方法

        :param url:
        :param browser:
        :return: pandas dataframe
        """
        raise Exception('子类需要实现本函数，返回需要数据的dataframe！')

    class Meta:
        abstract = True


class HSGTCG(HSGTCGBase):
    """ 沪深港通持股
    附注:

    1、基础数据来自港交所披露，数据展示港交所中央结算系统参与者于该日日终的持股量。如果所选择的持股日期是星期日或香港公共假期，则会显示最后一个非星期日或香港公共假期的持股记录。

    2、沪股通持股和深股通持股合成北向持股，港股通（沪）和港股通（深）合称南向持股。

    3、持股占A股百分比或者持股占发行股份百分比是按交易所相关上市公司的上市及交易的股总数而计算，有可能沒有包括公司实时动态变化，因此可能不是最新的。该数值只作为参考之用，使用该百分比时敬请注意。

    """

    code = models.CharField(verbose_name='代码', max_length=10, db_index=True, null=True)
    close = models.DecimalField(verbose_name='收盘价', max_digits=9, decimal_places=3, null=True)
    hvol = models.DecimalField(verbose_name='持股数量', max_digits=10, decimal_places=1, null=True)
    hamount = models.DecimalField(verbose_name='持股金额', max_digits=10, decimal_places=1, null=True)
    hpercent = models.DecimalField(verbose_name='持股数量占A股百分比', max_digits=6, decimal_places=3, null=True)
    tradedate = models.DateField(verbose_name='日期', null=True)

    @classmethod
    def getlist(cls, code=None):
        """
        返回stock_category类型列表

        :param stock_category: 证券类型
            STOCK_CATEGORY = ((10, "股票"),
                  (11, "指数"),
                  (12, "分级基金"),
                  (13, "债券"),
                  (14, "逆回购"),)
        :return: .objects.all().filter(category=stock_category)
        """
        if code:
            # 返回所有代码
            return cls.objects.all().filter(code=code)

        return cls.objects.all()

    def __str__(self):
        return '{} {} {} {}'.format(self.code, self.close, self.hvol, self.hamount)

    class Meta:
        verbose_name = '沪深港通持股'
        unique_together = (('code', 'tradedate'))


class HSGTCGHold(HSGTCGBase):
    """ 持股市值七千万

    """
    code = models.CharField(verbose_name='代码', max_length=10, db_index=True, null=True)
    tradedate = models.DateField(verbose_name='日期', null=True)

    @classmethod
    def importList(cls):
        browser = cls.getBrowser()
        url = 'http://data.eastmoney.com/hsgtcg/StockStatistics.aspx'
        df = cls.scrap(url, browser)
        # pandas dataframe save to model
        HSGTCGHold.objects.bulk_create(
            HSGTCGHold(**vals) for vals in df[['code', 'tradedate']].to_dict('records')
        )

    @staticmethod
    def scrap(url, browser):
        try:
            results = []
            pages = range(1, 37, 1)
            browser.get(url)
            # 北向持股
            browser.find_element_by_css_selector('.border_left_1').click()
            time.sleep(2)
            # 市值排序
            browser.find_element_by_css_selector(
                '#tb_ggtj > thead:nth-child(1) > tr:nth-child(1) > th:nth-child(8)').click()
            time.sleep(1.5)
            for page in pages:
                soup = BeautifulSoup(browser.page_source, 'lxml')
                table = soup.find_all(id='tb_ggtj')[0]
                df = pd.read_html(str(table), header=1)[0]
                df.columns = ['tradedate', 'code', 'name', 'a1', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday',
                              'fiveday',
                              'tenday']
                # 修复code长度，前补零
                df['code'] = df.code.astype(str)
                df['code'] = df['code'].apply(lambda x: x.zfill(6))
                # 修复持股数量
                df['hvol'] = df['hvol'].apply(lambda x: HSGTCGHold.hz2Num(x)).astype(float)
                df['hamount'] = df['hamount'].apply(lambda x: HSGTCGHold.hz2Num(x)).astype(float)
                # 删除多余的列
                del df['oneday']
                del df['fiveday']
                del df['tenday']
                del df['a1']
                results.append(df[df['hamount'] > MINHAMOUNT])
                if len(df[df['hamount'] < MINHAMOUNT]):
                    # 持股金额小于
                    break
                else:
                    # 下一页
                    t = browser.find_element_by_css_selector('#PageContgopage')
                    t.clear()
                    t.send_keys(str(page + 1))
                    browser.find_element_by_css_selector('.btn_link').click()

                    time.sleep(1.5)
                # print('results\n{}'.format(results))

        finally:
            if browser:
                browser.close()
        #  results 整合
        dfn = pd.DataFrame()
        for dfa in results:
            dfn = pd.concat([dfn, dfa])
        dfn.reset_index(drop=True, inplace=True)
        return dfn

    @classmethod
    def getlist(cls, tradedate=None):
        """
        返回stock_category类型列表

        :param stock_category: 证券类型
            STOCK_CATEGORY = ((10, "股票"),
                  (11, "指数"),
                  (12, "分级基金"),
                  (13, "债券"),
                  (14, "逆回购"),)
        :return: .objects.all().filter(category=stock_category)
        """
        if tradedate:
            # 返回所有代码
            from stocks.models import convertToDate
            return cls.objects.all().filter(tradedate=convertToDate(tradedate))

        return cls.objects.all()

    def __str__(self):
        return '{} {}'.format(self.code, self.tradedate)

    class Meta:
        verbose_name = '沪深港通持股列表'
        unique_together = (('code', 'tradedate'))
