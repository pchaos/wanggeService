# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hsgtcgNorthMoney
   Description :
   Author :       pchaos
   date：          18-12-14
-------------------------------------------------
   Change Activity:
                   18-12-14:
-------------------------------------------------
"""
__author__ = 'pchaos'

import time
import pandas as pd
from .eastmoneyBase import EASTMONEY


class HSGTCGNorthMoney(EASTMONEY):

    def prepareEnv(self):
        ''' 获取数据前的准备工作

        :return:
        '''
        if self.driver:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 执行JavaScript实现网页下拉倒底部
            time.sleep(0.5)
            # 持股市值排序
            self.driver.find_element_by_css_selector(
                '#tb_ggtj > thead > tr:nth-child(1) > th:nth-child(8) > span').click();

            # self.driver.find_element_by_xpath(
            #     u"(.//*[normalize-space(text()) and normalize-space(.)='近30日'])[1]/following::span[1]").click()
            # 自定义区间
            self.driver.find_element_by_xpath('//*[@id="filter_ggtj"]/div[2]/ul/li[6]/span').click()

            # 设置自定义时间区间
            dateScript = '''
            el = document.querySelectorAll('#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.date-input-wrap > input.date-input.date-search-start');
            el[0].value ='2018-12-10';
            el = document.querySelectorAll('#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.date-input-wrap > input.date-input.date-search-end');
            el[0].value ='2018-12-10';
    
            '''
            self.driver.execute_script(dateScript)
            self.driver.find_element_by_xpath('//*[@id="filter_ggtj"]/div[2]/ul/li[7]/div[1]/input[1]').click()
            # 点击查询
            self.driver.find_element_by_css_selector(
                '#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.search-btn').click();

    def getData(self):
        ''' 获取数据

        :return:
        '''
        return pd.DataFrame()
