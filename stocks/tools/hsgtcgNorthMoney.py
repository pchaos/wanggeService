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

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from bs4 import BeautifulSoup
import unittest, time, re


class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        # AppDynamics will automatically override this web driver
        # as documented in https://docs.appdynamics.com/display/PRO44/Write+Your+First+Script
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.eastmoney.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_app_dynamics_job(self):
        driver = self.driver
        driver.get("http://data.eastmoney.com/hsgtcg/StockStatistics.aspx")
        # driver.get("http://data.eastmoney.com/hsgtcg/")
        # driver.find_element_by_link_text(u"点击查看全部>>").click()
        # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | win_ser_1 | ]]
        # driver.find_element_by_xpath("//body").click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 执行JavaScript实现网页下拉倒底部
        time.sleep(0.5)
        # 持股市值排序
        driver.find_element_by_css_selector('#tb_ggtj > thead > tr:nth-child(1) > th:nth-child(8) > span').click();

        # driver.find_element_by_xpath(
        #     u"(.//*[normalize-space(text()) and normalize-space(.)='近30日'])[1]/following::span[1]").click()
        # 自定义区间
        driver.find_element_by_xpath('//*[@id="filter_ggtj"]/div[2]/ul/li[6]/span').click()

        # 第一个时间选择
        dateScript='''
        el = document.querySelectorAll('#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.date-input-wrap > input.date-input.date-search-start');
        el[0].value ='2018-12-10';
        el = document.querySelectorAll('#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.date-input-wrap > input.date-input.date-search-end');
        el[0].value ='2018-12-10';
        
        '''
        driver.execute_script(dateScript)
        driver.find_element_by_xpath('//*[@id="filter_ggtj"]/div[2]/ul/li[7]/div[1]/input[1]').click()
        # 点击查询
        driver.find_element_by_css_selector(
            '#filter_ggtj > div.cate_type > ul > li.custom-date-search.end > div.search-btn').click();

        driver.find_element_by_xpath("//body").click()
        driver.find_element_by_link_text(u"下一页").click()
        driver.find_element_by_link_text(u"下一页").click()
        # time.sleep(2)


    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        # To know more about the difference between verify and assert,
        # visit https://www.seleniumhq.org/docs/06_test_design_considerations.jsp#validating-results
        self.assertEqual([], self.verificationErrors)
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
