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

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time

__author__ = 'pchaos'


class TestHSGTCGHold(TestCase):
    def test_stockstatistics(self):
        """ 北持股向市值大于八千万

        :return:
        """

        def f(astr):
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

        opts = Options()
        opts.set_headless()
        assert opts.headless  # operating in headless mode
        browser = webdriver.Firefox()
        browser.maximize_window()
        try:
            results = []
            pages = range(1, 37, 1)
            page = 1
            # url = 'http://data.eastmoney.com/hsgtcg/StockStatistics.aspx?tab={}'.format(page)
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
                df['hvol'] = df['hvol'].apply(lambda x: f(x)).astype(float)
                df['hamount'] = df['hamount'].apply(lambda x: f(x)).astype(float)
                # 删除多余的列
                del df['oneday']
                del df['fiveday']
                del df['tenday']
                del df['a1']
                results.append(df[df['hamount'] > 8000])
                if len(df[df['hamount'] < 8000]):
                    # 持股金额小于
                    break
                else:
                    # 下一页
                    t = browser.find_element_by_css_selector('#PageContgopage')
                    t.clear()
                    t.send_keys(str(page + 1))
                    browser.find_element_by_css_selector('.btn_link').click()

                    time.sleep(1.5)
                # print(df)
                print('results\n{}'.format(results))

        finally:
            if browser:
                browser.close()
                pass
        self.assertTrue(len(results) > 3)
        # todo results 整合
        dfn = pd.DataFrame()
        for dfa in results:
            dfn = pd.concat([dfn, dfa])
        dfn.reset_index(drop=True, inplace=True)
        self.assertFalse(dfn[['code', 'tradedate']] is None)
        # pandas dataframe save to model
        HSGTCGHold.objects.bulk_create(
            HSGTCGHold(**vals) for vals in dfn[['code', 'tradedate']].to_dict('records')
        )
        self.assertTrue(HSGTCGHold.getlist().count() > 0, '北向持股大于七千万的股票数量大于0')
        print(HSGTCGHold.getlist())
