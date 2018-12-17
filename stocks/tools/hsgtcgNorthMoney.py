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
    # def __init__(self, url='', webdriverType='firefox', headless=False, waitTimeout=30, autoCloseWebDriver=True, minimumHoldAmount=5000):
    #     self.minimumHoldAmount = minimumHoldAmount
    #     super().__init__(url, webdriverType. headless, waitTimeout, autoCloseWebDriver)


    @property
    def minimumHoldAmount(self):
        '''
        最低持股市值
        :return:
        '''
        try:
            self.__minimumHoldAmount
        except NameError:
            self.__minimumHoldAmount = 50000
        return self.__minimumHoldAmount

    @minimumHoldAmount.setter
    def minimumHoldAmount(self, value):
        self.__minimumHoldAmount = value

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
            time.sleep(0.5)
            self.driver.find_element_by_xpath('//*[@id="filter_ggtj"]/div[2]/ul/li[6]/span').click()

            # 设置自定义时间区间
            dateScript = '''
            el = document.querySelectorAll('#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.date-input-wrap > input.date-input.date-search-start');
            el[0].value = ':date-search-start';
            el = document.querySelectorAll('#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.date-input-wrap > input.date-input.date-search-end');
            el[0].value = ':date-search-end';
            '''
            thedate = self.getTradeDate()
            dateScript = dateScript.replace(":date-search-start", thedate).replace(":date-search-end", thedate)
            # print('dateScript: {}'.format(dateScript))
            self.driver.execute_script(dateScript)
            self.driver.find_element_by_xpath('//*[@id="filter_ggtj"]/div[2]/ul/li[7]/div[1]/input[1]').click()
            # 点击查询
            self.driver.find_element_by_css_selector(
                '#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.search-btn').click();

    def getTradeDate(self):
        '''
        根据条件计算需要查询的交易日期
        :return:
        '''
        # todo 根据条件计算日期
        thedate = "2018-12-14"
        return thedate

    def getData(self):
        ''' 获取数据

        :return:
        '''
        alist = []
        self.columns = ['tradedate', 'code', 'name', 'hamount']
        df = pd.DataFrame(columns=self.columns)
        while True:

            df = self.getCurentPageData()
            alist.append(df[df['hamount'] >= self.minimumHoldAmount])
            time.sleep(0.8)
            if len(df[df['hamount'] < self.minimumHoldAmount]) < 1:
                # 满足市值条件，继续翻页查询
                self.nextPage()
            else:
                break
        # dataframe合并
        df = pd.DataFrame(columns=self.columns)
        for d in alist:
            df = pd.concat([df, d], ignore_index=True)
        self.save(df, '{}北向资金{}.EBK'.format('/dev/shm/temp/', self.getTradeDate()))
        return df

    def getCurentPageData(self):
        df = pd.DataFrame()
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
                # df['hvol'] = df['hvol'].apply(lambda x: EASTMONEY.hz2Num(x)).astype(float)
                df['hamount'] = df['hamount'].apply(lambda x: EASTMONEY.hz2Num(x)).astype(float)
                # df['close'] = df['close'].astype(float)
                df['code'] = df['code'].apply(lambda x: '{}'.format(x).zfill(6))
                df['tradedate'] = df['tradedate'].apply(lambda x: convertToDate(x)).astype(datetime.date)
                # df = pd.RangeIndex(len(df.index))
            except Exception as e:
                # 忽略异常数据
                print(e.args)
                print(df['code'][0], df)
        else:
            pass
        return df[self.columns]

    def save(self, df=None, fileName='/dev/shm/temp/test.csv'):
        if isinstance(df, pd.DataFrame):
            with open(fileName, 'w') as f:
                for item in df.code.values.tolist():
                    f.write("{}\n".format('1{}'.format(item) if item[0] == '6' else '0{}'.format(item)))
            return True
        else:
            return False

