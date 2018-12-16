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

from selenium import webdriver
from retrying import retry

__author__ = 'pchaos'

class EASTMONEY(metaclass=ABCMeta):
    ''' 东方财富爬取基类

    '''
    def __init__(self, url='', webdriverType='firefox', headless=False, waitTimeout=30):
        if self._checkUrl(url):
            self.base_url = url
        else:
            raise Exception('url不能为空！')
        # AppDynamics will automatically override this web driver
        # as documented in https://docs.appdynamics.com/display/PRO44/Write+Your+First+Script
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
            self.driver.find_element_by_link_text(u"下一页").click()

    def __del__(self):
        if self.driver:
            self.driver.close()