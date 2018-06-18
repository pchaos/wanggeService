# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_HSGTCGHold.py

Description :

@Author :       pchaos

date：          2018-5-31
-------------------------------------------------
Change Activity:
               18-5-31:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import HSGTCGHold
from stocks.models import Stocktradedate
from stocks.models import convertToDate

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime, time

__author__ = 'pchaos'


class TestHSGTCGHold(TestCase):
    def test_webdriver(self):
        browser = webdriver.Firefox()
        browser.maximize_window()
        try:
            url = 'http://data.eastmoney.com/hsgtcg/StockStatistics.aspx'
            browser.get(url)
            # 北向持股
            browser.find_element_by_css_selector('.border_left_1').click()
            time.sleep(0.2)
            # 自定义区间
            browser.find_element_by_css_selector('.custom-text > span:nth-child(1)').click()
            time.sleep(0.5)
            # 开始日期赋值
            tdate = browser.find_element_by_css_selector('input.date-input:nth-child(1)')
            tdate.send_keys(str(datetime.datetime.now().date()-datetime.timedelta(10)))
            time.sleep(0.5)
            tdate = browser.find_element_by_css_selector('.search-btn')
            time.sleep(5)

        finally:
            if browser:
                browser.close()

    def test_stockstatistics(self):
        """ 北向持股向市值大于八千万

        :return:
        """
        browser = webdriver.Firefox()
        browser.maximize_window()
        try:
            results = []
            pages = range(1, 37, 1)
            pages = range(1, 250, 1)  # 30日市值排序
            url = 'http://data.eastmoney.com/hsgtcg/StockStatistics.aspx'
            browser.get(url)
            # 北向持股
            browser.find_element_by_css_selector('.border_left_1').click()
            time.sleep(2)
            # 市值排序
            browser.find_element_by_css_selector(
                '#tb_ggtj > thead:nth-child(1) > tr:nth-child(1) > th:nth-child(8)').click()
            time.sleep(1.5)
            # 近30日
            browser.find_element_by_css_selector('.cate_type_ul > li:nth-child(5) > span:nth-child(1)').click()
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
                results.append(df[df['hamount'] >= 8000])
                if len(df[df['hamount'] < 8000]):
                    # 持股金额小于
                    break
                else:
                    # 下一页
                    t = browser.find_element_by_css_selector('#PageContgopage')
                    t.clear()
                    t.send_keys(str(page + 1))
                    btnenable = True
                    while btnenable:
                        try:
                            btn = browser.find_element_by_css_selector('.btn_link')
                            btn.click()
                            btnenable = False
                        except Exception as e:
                            print('not ready click. Waiting')
                            time.sleep(0.1)

                    time.sleep(1.5)
                # print(df)
                print('results\n{}'.format(results))

        finally:
            if browser:
                browser.close()
        self.assertTrue(len(results) > 3)
        #  results 整合
        dfn = pd.DataFrame()
        for dfa in results:
            dfn = pd.concat([dfn, dfa])
        dfn.reset_index(drop=True, inplace=True)
        self.assertFalse(dfn[['code', 'tradedate']] is None)
        df = dfn[['code', 'tradedate']]
        # 去除重复数据
        df = df[~df.duplicated()]
        HSGTCGHold.savedf(df[['code', 'tradedate']])
        # pandas dataframe save to model
        # HSGTCGHold.objects.bulk_create(
        #     HSGTCGHold(**vals) for vals in df[['code', 'tradedate']].to_dict('records'))
        self.assertTrue(HSGTCGHold.getlist().count() > 0, '北向持股大于七千万的股票数量大于0')
        print(HSGTCGHold.getlist())

    def test_importList(self):
        HSGTCGHold.importList()
        hsg = HSGTCGHold.getlist(tradedate=datetime.datetime.now().date() - datetime.timedelta(1))
        self.assertTrue(hsg.count() > 10, '北向持股大于七千万的股票数量大于10, 实际数量：{}'.format(hsg.count()))
        self.assertTrue(isinstance(hsg[0].tradedate, datetime.date))

    def test_loadModelfromFile(self):
        filename = 'HSGTCGHold_2018-06-01.pkl.gz'
        df = pd.read_pickle(filename)
        entries = df.to_dict('records')
        for v in entries:
            # print(v)
            HSGTCGHold.objects.get_or_create(**v)
        # 测试重复插入
        for v in entries:
            HSGTCGHold.objects.get_or_create(**v)
        print(HSGTCGHold.getlist().count())
        self.assertTrue(HSGTCGHold.getlist().count() > 100, '实际插入：{}'.format(HSGTCGHold.getlist().count()))

    def test_getRecentlist(self):
        Stocktradedate.importList()
        n = set(list(HSGTCGHold.getRecentlist().values_list('tradedate')))
        self.assertTrue(len(n) <= 1, '交易日:{}'.format(n))
        days = 3
        n = set(list(HSGTCGHold.getRecentlist().values_list('tradedate')))
        self.assertTrue(len(n) <= days, '交易日:{}'.format(n))
        days = 10
        n = set(list(HSGTCGHold.getRecentlist().values_list('tradedate')))
        self.assertTrue(len(n) <= days, '交易日:{}'.format(n))

    def test_deleteNotTradedate(self):
        # 删除不是交易日的数据
        for d in set(list(HSGTCGHold.objects.all().values_list('tradedate'))):
            if not Stocktradedate.if_tradeday(d[0]):
                HSGTCGHold.getlist(d[0]).delete()


    def test_newcomingin(self):
        """ 新加入市值八千万的个股

        :return:
        """
        Stocktradedate.importList()
        from stocks.models import HSGTCG
        #  2018 - 06 - 04 新增北向持股金额大于八千万
        list1 = ['603658' , '600460', '002812', '002557', '600188', '000690', '600329']

        tdate = HSGTCGHold.getNearestTradedate()
        # tdate = HSGTCGHold.getNearestTradedate('2018-6-4')
        tdate1 = HSGTCGHold.getNearestTradedate(tdate-datetime.timedelta(1))
        hsg = HSGTCGHold.getlist(tdate)
        hsg1 = HSGTCGHold.getlist(tdate1)
        list2 = []
        for c in hsg.exclude(code__in=hsg1.values_list('code')):
            list2.append(c.code)
        # 验证是否前一天市值小于八千万
        for code in list2:
            df =pd.DataFrame(list(HSGTCG.getlist(code).filter(tradedate__gte=tdate1).values().order_by('-tradedate')))
            data1= float(df.iloc[-2].hamount)
            data2= float(df.iloc[-1].hamount)
            if not (data1 >= 8000 and data2 < 8000):
                print('不是新增持股金额大于八千万：{} 持股金额：{} {}'.format(code, data1, data2))

        tdate = HSGTCGHold.getNearestTradedate()
        while tdate > convertToDate('2018-5-2'):
            tdate1 = HSGTCGHold.getNearestTradedate(tdate - datetime.timedelta(1))
            hsg = HSGTCGHold.getlist(tdate)
            hsg1 = HSGTCGHold.getlist(tdate1)
            list2 = []
            for c in hsg.exclude(code__in=hsg1.values_list('code')):
                list2.append(c.code)
            # 验证是否前一天市值小于八千万
            for code in list2:
                df = pd.DataFrame(
                    list(HSGTCG.getlist(code).filter(tradedate__gte=tdate1).values().order_by('-tradedate')))
                if len(df)> 1 and HSGTCG.getlist().filter(tradedate=tdate1).count() > 0:
                # if len(df)> 1 :
                    data1 = float(df.iloc[-2].hamount)
                    data2 = float(df.iloc[-1].hamount)
                    if not (data1 >= 8000 and data2 < 8000):
                        print('{} 不是新增持股金额大于八千万：{} 持股金额：{} {}'.format(tdate, code, data1, data2))
            tdate = HSGTCGHold.getNearestTradedate(tdate - datetime.timedelta(1))

    def test_directscrap(self):
        # http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/get?type=HSGTHDSTA&token=70f12f2f4f091e459a279469fe49eca5&st=SHAREHOLDPRICE&sr=-1&p=2&ps=50&js=var%20AtvxLaxn={pages:(tp),data:(x)}&filter=(MARKET%20in%20(%27001%27,%27003%27))(HDDATE%3E=^2018-05-28^%20and%20HDDATE%3C=^2018-06-07^)&rt=50948590
        import  requests, json
        pagesize = 100
        page = 1
        sr=3
        start = HSGTCGHold.getNearestTradedate() -datetime.timedelta(20)
        end = start + datetime.timedelta(10)
        if page > 1:
            sr = -1
        url ='http://dcfm.eastmoney.com//em_mutisvcexpandinterface/api/js/\
        get?type=HSGTHDSTA&token=70f12f2f4f091e459a279469fe49eca5&st=HDDATE,SHAREHOLDPRICE&sr={sr}\
        &p={page}&ps={pagesize}&js=var%20CiydgPzJ={pages:(tp),data:(x)}&filter=(MARKET%20in%20(%27001%27,%27003%27))\
        (HDDATE%3E=^{start}^%20and%20HDDATE%3C=^{end}^)&rt=50945623'\
            .replace('{start}', str(start)).replace('{end}', str(end))\
            .replace('{pagesize}', str(pagesize))\
            .replace('{page}', str(page))\
            .replace('{sr}', str(sr))
        response = requests.get(url, timeout=60)

        response = response.content.decode()
        data = response
        # data = data[len('var CiydgPzJ='):len(response) - 2]
        data = data[len('var CiydgPzJ='):]
        data_list = json.loads(data.replace('pages', '"pages"').replace('data',' "data"'))
        df = pd.DataFrame(data_list['data'])

    def test_everydayCount(self):
        Stocktradedate.importList()
        for d in [d[0] for d in set(list(HSGTCGHold.getlist().values_list('tradedate')))]:
            dcount = HSGTCGHold.getlist(d).count()
            print(d, dcount)

        from stocks.models import HSGTCG
        tdate = HSGTCGHold.getNearestTradedate()
        while tdate > convertToDate('2018-5-1'):
            dcount = HSGTCGHold.getlist(tdate).count()
            dcount1 = HSGTCG.getlist().filter(tradedate=tdate, hamount__gte=8000).count()
            print(tdate, dcount, dcount1, dcount - dcount1)
            tdate = HSGTCGHold.getNearestTradedate(tdate - datetime.timedelta(1))

        from stocks.models import HSGTCG
        tdate = HSGTCGHold.getNearestTradedate()
        while tdate > convertToDate('2018-5-1'):
            df1 = pd.DataFrame(list(HSGTCGHold.getlist(tdate).values('code')))
            dcount = len(df1)
            df2 = pd.DataFrame(list(HSGTCG.getlist().filter(tradedate=tdate, hamount__gte=8000).values('code')))
            dcount1 = len(df2)
            print(tdate, dcount, dcount1, dcount - dcount1)
            if dcount - dcount1 != 0 and tdate > convertToDate('2018-6-1'):
                print('数据不一致：', end='')
                print(list(HSGTCGHold.dfNotInAnotherdf(df1, df2)['code']))
            tdate = HSGTCGHold.getNearestTradedate(tdate - datetime.timedelta(1))