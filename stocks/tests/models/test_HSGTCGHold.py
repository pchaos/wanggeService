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

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import datetime, time

__author__ = 'pchaos'


class TestHSGTCGHold(TestCase):
    def test_stockstatistics(self):
        """ 北持股向市值大于八千万

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
                            btn=browser.find_element_by_css_selector('.btn_link')
                            btn.click()
                            btnenable =False
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
        # pandas dataframe save to model
        HSGTCGHold.objects.bulk_create(
            HSGTCGHold(**vals) for vals in df[['code', 'tradedate']].to_dict('records')
        )
        self.assertTrue(HSGTCGHold.getlist().count() > 0, '北向持股大于七千万的股票数量大于0')
        print(HSGTCGHold.getlist())

    def test_importList(self):
        HSGTCGHold.importList()
        hsg = HSGTCGHold.getlist(tradedate=datetime.datetime.now().date() - datetime.timedelta(1))
        self.assertTrue(hsg.count() > 10 , '北向持股大于七千万的股票数量大于10, 实际数量：{}'.format(hsg.count()))
        self.assertTrue(isinstance(hsg[0].tradedate, datetime.date))

    def test_loadModelfromFile(self):
        filename = 'HSGTCGHold_2018-06-01.pkl.gz'
        df =pd.read_pickle(filename)
        entries = df.to_dict('records')
        for v in entries:
            # print(v)
            HSGTCGHold.objects.get_or_create(**v)
        # 测试重复插入
        for v in entries:
            HSGTCGHold.objects.get_or_create(**v)
        print(HSGTCGHold.getlist().count())
        self.assertTrue(HSGTCGHold.getlist().count() > 100, '实际插入：{}'.format(HSGTCGHold.getlist().count()))