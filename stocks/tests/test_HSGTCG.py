# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_HSGTCG.py

Description :

@Author :       pchaos

date：          18-5-30
-------------------------------------------------
Change Activity:
               18-5-30:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import HSGTCG

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time

__author__ = 'pchaos'


def str2Float(astr):
    """ 包含汉字数字的字符串转为float

    :param astr:
    :return:
    """
    try:
        if type(astr) is str:
            y = '亿'
            if astr.find(y) >= 0:
                return float(astr.replace(y, '')) * 100000
    except:
        return 0


class TestHSGTCG(TestCase):
    def test_getlist(self):
        self.fail()

    def test_scrapt(self):
        """ 个股北向持股

        :return:
        """
        code = '600066'
        url = 'http://data.eastmoney.com/hsgtcg/StockHdStatistics.aspx?stock={}'.format(code)

        opts = Options()
        opts.set_headless()
        assert opts.headless  # operating in headless mode
        browser = webdriver.Firefox()
        browser.maximize_window()
        try:
            browser.get(url)
            soup = BeautifulSoup(browser.page_source, 'lxml')
            table = soup.find_all(id='tb_cgtj')[0]
            df = pd.read_html(str(table), header=1)[0]
            df.columns = ['date', 'related', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday', 'fiveday',
                          'tenday']
            for i in df.index:
                v = df.iloc[i]
                print('{} {} {} {}'.format(v.close, v.hvol, v.hamount, v.hpercent))
                HSGTCG.objects.get_or_create(code=code, close=v.close, hvol=str2Float(v.hvol),
                                             hamount=str2Float(v.hamount), hpercent=v.hpercent)
        finally:
            if browser:
                browser.close()
        hsgtcg = HSGTCG.getlist(code)
        # hsgtcg = HSGTCG.getlist()
        print(hsgtcg)
        self.assertTrue(hsgtcg.count() > 10, '保存的数量： {}'.format(hsgtcg.count()))

    def test_StockStatistics(self):
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
                        return str(np.round(float(astr)/10000, 2))
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
            url = 'http://data.eastmoney.com/hsgtcg/StockStatistics.aspx?tab={}'.format(page)
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
                df.columns = ['date', 'code', 'name', 'a1', 'close', 'zd', 'hvol', 'hamount', 'hpercent', 'oneday',
                              'fiveday',
                              'tenday']
                # 修复code长度，前补零
                df['code'] = df.code.astype(str)
                df['code'] = df['code'].apply(lambda x: x.zfill(6))
                # 修复持股数量
                df['hvol'] = df['hvol'].apply(lambda x: f(x)).astype(float)
                df['hamount'] = df['hamount'].apply(lambda x: f(x)).astype(float)
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
