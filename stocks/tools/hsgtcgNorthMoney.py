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

from bs4 import BeautifulSoup
import time, datetime
import pandas as pd
from .eastmoneyBase import EASTMONEY, convertToDate


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
        try:
            for x in ['lxml', 'xml', 'html5lib']:
                # 可能会出现lxml版本大于4.1.1时，获取不到table
                try:
                    soup = BeautifulSoup(self.driver.page_source, x)
                    table = soup.find_all(id='tb_ggtj')[0]
                    if table:
                        break
                except:
                    time.sleep(0.1)
                    print('Error using BeautifulSoup {}'.format(x))
            df = pd.read_html(str(table), header=1)[0]
            # 交易日期 代码 名称 其他 收盘价 涨跌百分比 持股数量（股） 持股市值（元） 持股数量占A股百分比(%) 持股市值变化（元）【一日 五日 十日】
            df.columns = ['tradedate', 'code', 'name', 'others', 'close', 'percent', 'hvol', 'hamount', 'hpercent',
                          'oneday', 'fiveday', 'tenday']
        except Exception as e:
            print(e.args)
            return pd.DataFrame()

        if len(df) > 0:
            try:
                # 修复持股数量
                df['hvol'] = df['hvol'].apply(lambda x: EASTMONEY.hz2Num(x)).astype(float)
                df['hamount'] = df['hamount'].apply(lambda x: EASTMONEY.hz2Num(x)).astype(float)
                df['close'] = df['close'].astype(float)
                df['code'] = df['code'].apply(lambda x: '{}'.format(x).zfill(6))
                df['tradedate'] = df['tradedate'].apply(lambda x: convertToDate(x)).astype(datetime.date)
                # df = df[df['tradedate'].apply(lambda x: Stocktradedate.if_tradeday(x))]  # 删除不是交易日的数据。这是东方财富网页版的bug
                # df = pd.RangeIndex(len(df.index))
            except Exception as e:
                # 忽略异常数据
                print(e.args)
                print(df['code'][0], df)
        else:
            pass
        return df
        # return pd.DataFrame()
