# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     eastmoneyBase
   Description :
   Author :       pchaos
   date：          18-12-16
-------------------------------------------------
   Change Activity:
                   18-12-16:
-------------------------------------------------
"""
from abc import ABCMeta, abstractmethod
import numpy as np
import datetime
from selenium import webdriver
from retrying import retry

__author__ = 'pchaos'

# 例如： 2017-01-01
DATE_FORMAT = '%Y-%m-%d'

def convertToDate(date, dateformat=DATE_FORMAT):
    """ 转换为日期类型

    :param date: DATE_FORMAT = '%Y-%m-%d'
    例如： '2017-01-01'

    :return:  返回日期 date.date()
    """
    try:
        date = datetime.datetime.strptime(date, dateformat)
        return date.date()
    except TypeError:
        return date

class EASTMONEY(metaclass=ABCMeta):
    ''' 东方财富爬取基类

    '''
    def __init__(self, url='', webdriverType='firefox', headless=False, waitTimeout=30, autoCloseWebDriver=True):
        '''

        :param url:
        :param webdriverType:
        :param headless:
        :param waitTimeout:
        :param autoCloseWebDriver: 是否自动关闭webdriver
        '''
        if self._checkUrl(url):
            self.base_url = url
        else:
            raise Exception('url不能为空！')
        self.autoCloseWebDriver = autoCloseWebDriver
        self.driver = webdriver.Firefox()
        if headless:
            pass
        else:
            self.driver.maximize_window()
        self.driver.implicitly_wait(waitTimeout)
        self.get(url)
        self.prepareEnv()

    @retry(stop_max_attempt_number=3)
    def get(self, url):
        return self.driver.get(url)

    def _checkUrl(self, url):
        if len(url) > 0:
            return True
        else:
            return False

    @abstractmethod
    def prepareEnv(self):
        ''' 获取数据前的准备工作，子类需要继承此方法

        :return:
        '''
        pass

    @abstractmethod
    def getData(self):
        ''' 获取数据

        :return:
        '''
        pass

    def nextPage(self):
        if self.driver:
            nextp=self.driver.find_element_by_link_text(u"下一页")
            if nextp:
                nextp.click()
            return nextp

    @abstractmethod
    def save(self, df=None, fileName='/dev/shm/temp/test.csv'):
        '''
        保存结果
        :param df:
        :param fileName:
        :return:
        '''
        pass

    def __del__(self):
        if self.autoCloseWebDriver and self.driver:
            self.driver.close()

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
                    return str(np.round(float(astr.replace(y, '')) * 10000, 2))
                y = '万'
                if astr.find(y) >= 0:
                    return str(np.round(float(astr.replace(y, '')), 2))
                else:
                    return str(np.round(float(astr) / 10000, 2))
        except:
            return '0'