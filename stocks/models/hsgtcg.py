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
MINHAMOUNT = 8000  # 最小关注的北向持仓金额

from django.db import models
from django.db import transaction
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
# import re
import pandas as pd
import numpy as np
import time, datetime
from .stocktradedate import Stocktradedate
from stocks.models import convertToDate
import os


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
    def str2Float(astr):
        """ 包含汉字数字的字符串转为float

        :param astr:
        :return:
        """
        try:
            if type(astr) is str:
                y = '亿'
                if astr.find(y) >= 0:
                    return round(float(astr.replace(y, '')) * 100000, 2)
                y = '万'
                if astr.find(y) >= 0:
                    return round(float(astr.replace(y, '')), 2)
                else:
                    return round(float(astr) / 10000, 2)
        except:
            return 0

    @staticmethod
    def getBrowser(headless=None):
        """ 获取webdriver浏览器

        :param headless: 是否无窗口模式
        :return: browser
        """
        opts = Options()
        if headless:
            opts.set_headless()
            # opts.add_argument('-headless')
        # assert opts.headless  # operating in headless mode
        # browser = webdriver.Firefox()
        browser = webdriver.Firefox(firefox_options=opts)
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

    @staticmethod
    def getNearestTradedate(date=datetime.datetime.now().date()):
        """ 获取离date最近的交易日期
            只能获取到前一交易日的数据

        :param date:
        :return:
        """
        date = convertToDate(date)
        tradedate = Stocktradedate.get_real_date(date, -1).date()

        if date == tradedate:
            if date == datetime.datetime.now().date():
                # 当天并且是交易日
                tradedate = Stocktradedate.preTradeday(tradedate)
        return tradedate

    @classmethod
    def getlist(cls, tradedate=None):
        """
        返回列表

        :param tradedate: 交易日期

        :return: objects.all().filter(tradedate=convertToDate(tradedate))
        """
        if tradedate:
            # 返回所有代码
            # from stocks.models import convertToDate
            return cls.objects.all().filter(tradedate=convertToDate(tradedate))

        return cls.objects.all()

    @classmethod
    def getRecentlist(cls, days=1):
        """ 返回最近days天列表

        :param days: 之前几个交易

        :return: .objects.all().filter(tradedate__gte=tdate)
        """
        if days == 0:
            return cls.objects.all()
        else:
            tdate = cls.getNearestTradedate()
            if days > 1:
                realdatelist = Stocktradedate.get_real_datelisting(tdate - datetime.timedelta(days * 2 + 10), tdate)
                tdate = pd.DataFrame(list(realdatelist.order_by('id').values_list('tradedate'))).iloc[-days][0]
            # 返回所有代码
            return cls.objects.all().filter(tradedate__gte=tdate)

    @classmethod
    def saveModel2File(cls, filename=None, dropPk=True):
        if not filename:
            filename = '{}_{}.pkl.gz'.format(cls.__name__, datetime.datetime.now().date())
        from django.forms import model_to_dict
        aobjs = [model_to_dict(aobj) for aobj in cls.objects.all()]
        df = pd.DataFrame(aobjs)
        cls.dropDataframePK(df, dropPk)
        df.to_pickle(filename)
        return filename

    @classmethod
    def loadModelFromFile(cls, filename=None, dropPk=True):
        if filename:
            df = pd.read_pickle(filename)
            cls.dropDataframePK(df, dropPk)
            entries = df.to_dict('records')
            with transaction.atomic():
                for v in entries:
                    cls.objects.get_or_create(**v)
        else:
            print('文件名为空，请传正确的文件名！')

    @classmethod
    def dropDataframePK(cls, df, dropPk):
        """ 删除无明确意义的主键字段.
        如果是有业务逻辑意义的主键不能删除

        :param df:
        :param dropPk:
        :return:
        """
        if dropPk:
            pkname = 'id'
            if pkname in list(df.columns):
                #  主键在保存的dataFrame中
                df.drop(pkname, axis=1, inplace=True)

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
        返回沪深港通持股大于某个金额的列表

        :param code:
        :return:
        """
        if code:
            # 返回所有代码为code的列表
            return cls.objects.all().filter(code=code)

        return cls.objects.all()

    @classmethod
    def importList(cls, firefoxHeadless=True):
        """ 根据最近交易日的持仓交恶，获取相应的个股北向数据

        :param firefoxHeadless: 是否显示浏览器界面：
            True  不显示界面
            False 显示界面
            默认不显示浏览器界面

        :return:
        """
        hsgh = HSGTCGHold.getlist(tradedate=cls.getNearestTradedate())
        if hsgh.count() == 0:
            HSGTCGHold.importList()
            hsgh = HSGTCGHold.getlist(tradedate=cls.getNearestTradedate())
        browser = cls.getBrowser(firefoxHeadless)
        try:
            for code in [code[0] for code in list(hsgh.values_list('code'))]:
                dfd = pd.DataFrame(list(HSGTCG.getlist().filter(code=code).values('tradedate')))
                url = 'http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}'.format(code)
                df = cls.scrap(url, browser)
                # 修复持股数量
                df['hvol'] = df['hvol'].apply(lambda x: HSGTCG.hz2Num(x)).astype(float)
                df['hamount'] = df['hamount'].apply(lambda x: HSGTCG.hz2Num(x)).astype(float)
                df['close'] = df['close'].astype(float)
                df['date'] = df['date'].apply(lambda x: convertToDate(x)).astype(datetime.date)
                df = df[df['date'].apply(lambda x: Stocktradedate.if_tradeday(x))]  # 删除不是交易日的数据。这是东方财富网页版的bug
                df.index = pd.RangeIndex(len(df.index))
                with transaction.atomic():
                    for i in df.index:
                        v = df.iloc[i]
                        if len(dfd[dfd['tradedate'] == v.date]) > 0:
                            # 保存过的日期，或者不是交易日 pass
                            continue
                        # 没有保存过的日期
                        try:
                            print('{} saving ... {} {} {}'.format(cls.__name__, code, v.date, v.close))
                            HSGTCG.objects.get_or_create(code=code, close=v.close, hvol=v.hvol,
                                                         hamount=v.hamount, hpercent=v.hpercent,
                                                         tradedate=v.date)
                        except Exception as e:
                            # print(code[0], v, type(v.close), type(v.hpercent))
                            print(code[0], e.args)
                            # raise Exception(e.args)
        finally:
            if browser:
                browser.close()

    @staticmethod
    def scrap(url, browser):
        """ 抓取网页table

        :param url: 网址
        :param browser: 浏览器
        :return:
        """
        browser.get(url)
        time.sleep(0.1)
        soup = BeautifulSoup(browser.page_source, 'lxml')
        table = soup.find_all(id='tb_cgtj')[0]
        df = pd.read_html(str(table), header=1)[0]
        df.columns = ['date', 'related', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday', 'fiveday',
                      'tenday']
        return df

    def __str__(self):
        return '{} {} {} {} {}'.format(self.code, self.close, self.hvol, self.hamount, self.tradedate)

    class Meta:
        verbose_name = '沪深港通持股'
        unique_together = (('code', 'tradedate'))


class HSGTCGHold(HSGTCGBase):
    """ 持股市值八千万

    """
    code = models.CharField(verbose_name='代码', max_length=10, db_index=True, null=True)
    tradedate = models.DateField(verbose_name='日期', null=True)

    @classmethod
    def importList(cls, firefoxHeadless=False):
        """ 导入市值大于指定值的列表

        网址： http://data.eastmoney.com/hsgtcg/StockStatistics.aspx

        :param firefoxHeadless: 是否显示浏览器界面：
            True  不显示界面
            False 显示界面
            默认不显示浏览器界面

        :return: 最近交易日期的列表
        """
        hsgh = HSGTCGHold.getlist(tradedate=cls.getNearestTradedate())
        if hsgh.count() > 0:
            return hsgh
        browser = cls.getBrowser(firefoxHeadless)
        url = 'http://data.eastmoney.com/hsgtcg/StockStatistics.aspx'
        df = cls.scrap(url, browser)
        df = df[['code', 'tradedate']]
        df = df[df['tradedate'].apply(lambda x: Stocktradedate.if_tradeday(x))]
        # 去除重复数据
        df = df[~df.duplicated()]
        # pandas dataframe save to model
        HSGTCGHold.objects.bulk_create(
            HSGTCGHold(**vals) for vals in df[['code', 'tradedate']].to_dict('records')
        )
        return cls.getlist(tradedate=cls.getNearestTradedate())

    @staticmethod
    def scrap(url, browser):
        try:
            results = []
            pages = range(1, 37, 1)
            browser.get(url)
            # 北向持股
            browser.find_element_by_css_selector('.border_left_1').click()
            time.sleep(1.5)
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
                results.append(df[df['hamount'] >= MINHAMOUNT])
                if len(df[df['hamount'] < MINHAMOUNT]):
                    # 持股金额小于
                    break
                else:
                    # 下一页
                    print(' after page:{}'.format(page))
                    t = browser.find_element_by_css_selector('#PageContgopage')
                    t.clear()
                    t.send_keys(str(page + 1))
                    btnenable = True
                    while btnenable:
                        # 防止页面button失效的错误
                        try:
                            # 点击按钮“go”
                            browser.find_element_by_css_selector('.btn_link').click()
                            btnenable = False
                        except Exception as e:
                            print('not ready click. Waiting')
                            time.sleep(0.1)
                    time.sleep(1.3)
                    print('page:{}'.format(page + 1))
                # print('results\n{}'.format(results))

        finally:
            if browser:
                browser.close()
        #  results 整合
        dfn = pd.DataFrame()
        for dfa in results:
            dfn = pd.concat([dfn, dfa])
        dfn.reset_index(drop=True, inplace=True)
        # dfn.index = pd.RangeIndex(len(dfn.index))
        return dfn

    def __str__(self):
        return '{} {}'.format(self.code, self.tradedate)

    class Meta:
        verbose_name = '沪深港通持股列表'
        unique_together = (('code', 'tradedate'))
