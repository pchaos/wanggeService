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
import pandas as pd
import numpy as np
import time, datetime
from stocks.models import Stocktradedate
from stocks.models import convertToDate
from stocks.models import StockBase
import os


class HSGTCGBase(StockBase):
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
    def getBrowser(headless=None, pageloadtimeout=40):
        """ 获取webdriver浏览器

        :param headless: 是否无窗口模式
        :param pageloadtimeout: 加载页面超时（秒）
        :return: browser
        """
        opts = Options()
        if headless:
            opts.set_headless()
            # opts.add_argument('-headless')
        # assert opts.headless  # operating in headless mode
        # browser = webdriver.Firefox()
        browser = webdriver.Firefox(firefox_options=opts)
        browser.set_page_load_timeout(pageloadtimeout)
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

    class Meta:
        abstract = True


class HSGTCG(HSGTCGBase):
    """ 沪深港通持股
    附注:

    1、基础数据来自港交所披露，数据展示港交所中央结算系统参与者于该日日终的持股量。如果所选择的持股日期是星期日或香港公共假期，则会显示最后一个非星期日或香港公共假期的持股记录。

    2、沪股通持股和深股通持股合成北向持股，港股通（沪）和港股通（深）合称南向持股。

    3、持股占A股百分比或者持股占发行股份百分比是按交易所相关上市公司的上市及交易的股总数而计算，有可能沒有包括公司实时动态变化，因此可能不是最新的。该数值只作为参考之用，使用该百分比时敬请注意。

    东方财富北向查询
    http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock=600519

    json
    http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get?type=HSGTHDSTA&token=70f12f2f4f091e459a279469fe49eca5&filter=(SCODE='002081')&st={sortType}&sr={sortRule}&p={page}&ps={pageSize}&js=var {jsname}={pages:(tp),data:(x)}{param}
    http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get?type=HSGTHDSTA&token=70f12f2f4f091e459a279469fe49eca5&filter=(SCODE=%27002081%27)&st=HDDATE&sr=-1&p=1&ps=50&js=var%20JxagYxRi={pages:(tp),data:(x)}&rt=50951262

    深股通查询
    http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sz
    繁体版
    http://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sz

    沪股通
    http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh
    繁体版
    http://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh

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
    def importList(cls, firefoxHeadless=True, checkNearesttradeday=True):
        """ 根据最近交易日的持仓交恶，获取相应的个股北向数据

        :param firefoxHeadless: 是否显示浏览器界面：
            True  不显示界面
            False 显示界面
            默认不显示浏览器界面

        :param checkNearesttradeday: 是否检查最近交易日
            当checkNearesttradeday=True ，最近交易日有数据，则不检查此代码对应的网页

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
                if checkNearesttradeday:
                    if len(dfd) > 0:
                        if len(dfd[dfd['tradedate'] == cls.getNearestTradedate()]) > 0:
                            print('已保存最近交易日数据，跳过:{}'.format(code))
                            continue
                    else:
                        print('新加入北向持股大于{}万,请留意：{}'.format(MINHAMOUNT, code))
                df = cls.getStockHdStatistics(code, browser)
                with transaction.atomic():
                    for i in df.index:
                        v = df.iloc[i]
                        if len(dfd) > 0 and len(dfd[dfd['tradedate'] == v.tradedate]) > 0:
                            # 以前保存过，才需要判断保存过的交易日
                            # 保存过的日期，或者不是交易日 pass
                            continue
                        # 没有保存过的日期
                        try:
                            print('{} saving ... {} {} {}'.format(cls.__name__, code, v.tradedate, v.close))
                            HSGTCG.objects.get_or_create(code=code, close=v.close, hvol=v.hvol,
                                                         hamount=v.hamount, hpercent=v.hpercent,
                                                         tradedate=v.tradedate)
                        except Exception as e:
                            # print(code[0], v, type(v.close), type(v.hpercent))
                            print(code[0], e.args)
                            # raise Exception(e.args)
        finally:
            if browser:
                browser.close()

    @classmethod
    def getStockHdStatistics(cls, code, browser):
        """ 抓取持股统计

        :param code: 股票代码
        :param browser: webdriver浏览器
        :return:
        """
        url = 'http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}'.format(code)
        df = cls.scrap(url, browser)
        if len(df) > 0:
            # 修复持股数量
            df['hvol'] = df['hvol'].apply(lambda x: HSGTCG.hz2Num(x)).astype(float)
            df['hamount'] = df['hamount'].apply(lambda x: HSGTCG.hz2Num(x)).astype(float)
            df['close'] = df['close'].astype(float)
            df['tradedate'] = df['tradedate'].apply(lambda x: convertToDate(x)).astype(datetime.date)
            df = df[df['tradedate'].apply(lambda x: Stocktradedate.if_tradeday(x))]  # 删除不是交易日的数据。这是东方财富网页版的bug
            df.index = pd.RangeIndex(len(df.index))
        return df

    @staticmethod
    def scrap(url, browser):
        """ 抓取网页table

        :param url: 网址
        :param browser: 浏览器
        :return: dataframe
        """
        try:
            browser.get(url)
            time.sleep(0.03)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            table = soup.find_all(id='tb_cgtj')[0]
            df = pd.read_html(str(table), header=1)[0]
            df.columns = ['tradedate', 'related', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday', 'fiveday',
                          'tenday']
        except Exception as e:
            print(e.args)
            return pd.DataFrame()

        return df

    def __str__(self):
        return '{} {} {} {} {}'.format(self.code, self.close, self.hvol, self.hamount, self.tradedate)

    class Meta:
        verbose_name = '沪深港通持股'
        unique_together = (('code', 'tradedate'))


class HSGTCGHold(HSGTCGBase):
    """ 持股市值八千万

  http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get?type=HSGTHDSTA&token=70f12f2f4f091e459a279469fe49eca5&st=SHAREHOLDPRICE&sr=-1&p=5&ps=150&js=var%20CiydgPzJ={pages:(tp),data:(x)}&filter=(MARKET%20in%20(%27001%27,%27003%27))(HDDATE%3E=^2018-05-29^%20and%20HDDATE%3C=^2018-06-08^)&rt=50950960

    """
    code = models.CharField(verbose_name='代码', max_length=10, db_index=True, null=True)
    tradedate = models.DateField(verbose_name='日期', null=True)

    @classmethod
    def importList(cls, enddate=None, days=5, firefoxHeadless=True):
        """ 默认调用json模式
        当days为None时，调用importWebdriverList，使用webdriver方式

        :param enddate:
        :param days:
        :param firefoxHeadless:
        :return:
        """
        if days:
            return cls.importjsonList(enddate, days)
        else:
            return cls.importWebdriverList(firefoxHeadless)

    @classmethod
    def importWebdriverList(cls, firefoxHeadless=False):
        """ 导入市值大于指定值的列表

        网址： http://data.eastmoney.com/hsgtcg/StockStatistics.aspx

        不建议用此方法，经常丢失数据

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
        cls.savedf(df[['code', 'tradedate']])
        # pandas dataframe save to model
        # HSGTCGHold.objects.bulk_create(
        #     HSGTCGHold(**vals) for vals in df[['code', 'tradedate']].to_dict('records')
        # )
        return cls.getlist(tradedate=cls.getNearestTradedate())

    @classmethod
    def importjsonList(cls, enddate=None, days=5):
        """ 导入市值大于指定值的列表

        网址： http://data.eastmoney.com/hsgtcg/StockStatistics.aspx
        直接下载json文件转换，效率比importList高

        :param firefoxHeadless: 是否显示浏览器界面：
            True  不显示界面
            False 显示界面
            默认不显示浏览器界面

        :return: 最近交易日期的列表jsonname
        """
        if enddate:
            end = convertToDate(enddate)
        else:
            end = cls.getNearestTradedate()
            hsgh = cls.getlist(tradedate=end)
            if hsgh.count() > 0:
                return hsgh
        pagesize = 300  # 每页数据量
        page = 1
        sortRule = -1  # sortRule-1 按照市值降序排序； 1 按照市值升序排序

        start = end - datetime.timedelta(days)
        jsname = cls.getRandomStr('letter')
        for page in range(1, 100):
            if page > 1:
                sr = -1
            # st=SHAREHOLDPRICE 按照持股市值排序; st sortType
            url = 'http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/' \
                'get?type=HSGTHDSTA&token=70f12f2f4f091e459a279469fe49eca5&st=SHAREHOLDPRICE&sr={sortRule}' \
                '&p={page}&ps={pagesize}&js=var%20{jsname}={pages:(tp),data:(x)}&filter=(MARKET%20in%20(%27001%27,%27003%27))' \
                '(HDDATE%3E=^{start}^%20and%20HDDATE%3C=^{end}^)&rt=50950960' \
                .replace('{start}', str(start)).replace('{end}', str(end)) \
                .replace('{sortRule}', str(sortRule)) \
                .replace('{pagesize}', str(pagesize)) \
                .replace('{page}', str(page)) \
                .replace('{jsname}', str(jsname))
            df = cls.scrapjson(url)
            dfn = df[df['hamount'] >= MINHAMOUNT]
            if len(dfn) > 0:
                dfn = dfn[dfn['tradedate'].apply(lambda x: Stocktradedate.if_tradeday(x))]
                # 去除重复数据
                dfn = dfn[~dfn.duplicated()]
                cls.savedf(dfn[['code', 'tradedate']])
            print(page)
            if len(df[df['hamount'] < MINHAMOUNT]):
                # 持股金额小于
                break
        return cls.getlist(tradedate=cls.getNearestTradedate())

    @staticmethod
    def scrapjson(url):
        import requests, json

        # 异常处理 最多三次抓取
        for _ in range(3):
            try:
                response = requests.get(url, timeout=40)

                response = response.content.decode()
                data = response
                # data = data[len('var CiydgPzJ='):len(response) - 2]
                data = data[len('var CiydgPzJ='):]
                data_list = json.loads(data.replace('pages', '"pages"').replace('data', ' "data"'))
                df = pd.DataFrame(data_list['data'])
                df['code'] = df.SCODE.astype(str)
                df['hamount'] = df.SHAREHOLDPRICE.apply(lambda x: round(x/10000, 2)).astype(float)
                df['tradedate'] = df['HDDATE'].apply(lambda x: convertToDate(str(x)[:10])).astype(datetime.date)
                if len(df) > 0:
                    break
            except Exception as e:
                print('requests.get(url, timeout=40)\n{}'.format(e.args))
                time.sleep(1)
        return df[['code', 'tradedate', 'hamount']]

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
                # 删除多余的列reset_inde
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
                            time.sleep(0.15)
                    time.sleep(1.5)
                    print('page:{}'.format(page + 1))
                # print('results\n{}'.format(results))

        finally:
            if browser:
                browser.close()
        #  results 整合
        dfn = pd.DataFrame()
        for dfa in results:
            dfn = pd.concat([dfn, dfa])
        # dfn.reset_index(drop=True, inplace=True)
        dfn.index = pd.RangeIndex(len(dfn.index))
        return dfn

    def __str__(self):
        return '{} {}'.format(self.code, self.tradedate)

    class Meta:
        verbose_name = '沪深港通持股列表'
        unique_together = (('code', 'tradedate'))
