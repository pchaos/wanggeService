# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_get_proxy.py

Description :

@Author :       pchaos

date：          18-6-13
-------------------------------------------------
Change Activity:
               18-6-13:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from unittest import TestCase
from stocks.tools.proxy import get_proxy, delete_proxy
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

__author__ = 'pchaos'


def getHtml(url, proxy):
    retry_count = 3

    while retry_count > 0:
        try:
            html = requests.get(url, proxies={"http": "http://{}".format(proxy)}, timeout=25)
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 出错5次, 删除代理池中代理
    delete_proxy(proxy)
    return None

def getHtmlwithSocks(url, proxy):
    retry_count = 3

    while retry_count > 0:
        try:
            html = requests.get(url, proxies={"http": "socks5://{}".format(proxy),
                                              "https": "socks5://{}".format(proxy)}, timeout=25)
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    return None

class TestGet_proxy(TestCase):
    def test_get_proxy(self):
        proxy = get_proxy()
        self.assertTrue(len(proxy) > 10, '返回结果应大于十字节：{}'.format(proxy))
        proxyList = []
        n = 10
        for i in range(n):
            proxyList.append(get_proxy())
        self.assertTrue(len(set(proxyList)) == n, '每次返回值都应该不同：{}'.format(proxyList))

    def test_validproxy(self):
        list = []
        url = 'http://data.eastmoney.com/hsgtcg/StockHdDetail.aspx?stock=600519&date=2018-06-12'
        url = 'https://api.ipify.org/'
        for i in range(100):
            proxy = get_proxy().decode('utf-8')
            print('checking {}'.format(proxy))
            html = getHtml(url, proxy)
            if html.status_code and len(html.content) ==14:
                print('suscess')
                list.append(proxy)
            else:
                print('deleting')

    def test_validK3myproxy(self):
        list = []
        url = 'http://data.eastmoney.com/hsgtcg/StockHdDetail.aspx?stock=600519&date=2018-06-12'
        for i in range(2):
            proxy = "192.168.103.1:1081"
            print('checking {}'.format(proxy))
            if getHtmlwithSocks(url, proxy):
                print('suscess:\n{}'.format(getHtmlwithSocks(url, proxy)))
                print('length content:{}'.format(len(getHtmlwithSocks(url, proxy).content)))
                list.append(proxy)
            else:
                print('deleting')

    def test_validtorproxy(self):
        list = []
        url = 'http://data.eastmoney.com/hsgtcg/StockHdDetail.aspx?stock=600519&date=2018-06-12'
        url = 'https://api.ipify.org/'
        for i in range(2):
            proxy = "127.0.0.1:9150"
            print('checking {}'.format(proxy))
            if getHtmlwithSocks(url, proxy):
                print('suscess:\n{}'.format(getHtmlwithSocks(url, proxy)))
                print('content:{}'.format(getHtmlwithSocks(url, proxy).content))
                list.append(proxy)
                list.append(proxy)
            else:
                print('failed')
        time.sleep(5)

    def test_webdriver(self):
        from selenium.webdriver.common.proxy import Proxy, ProxyType
        myProxy = "127.0.0.1:8123"
        myProxy = "192.168.103.1:1081"
        desired_capability = webdriver.DesiredCapabilities.FIREFOX
        desired_capability['proxy'] = {
            "proxyType": "manual",
            "httpProxy": myProxy,
            "ftpProxy": myProxy,
            "sslProxy": myProxy
        }
        try:
            browser = webdriver.Firefox(capabilities=desired_capability, timeout=30)
            url = "http://data.eastmoney.com/hsgtcg/StockHdDetail.aspx?stock=600519&date=2018-06-12/"
            browser.get(url)
            time.sleep(25)
        finally:
            print(myProxy)
            browser.quit()

    def test_webdriver2(self):
        import time
        from selenium import webdriver

        fp = webdriver.FirefoxProfile()
        fp.set_preference('network.proxy.type', 1)
        fp.set_preference('network.proxy.socks', '127.0.0.1')
        fp.set_preference('network.proxy.socks_port', 9150)
        driver = webdriver.Firefox(fp)
        url = 'https://api.ipify.org'
        url = "http://data.eastmoney.com/hsgtcg/StockHdDetail.aspx?stock=600519&date=2018-06-12/"
        driver.get(url)
        print(driver.find_element_by_tag_name('pre').text)
        driver.get('https://check.torproject.org/')
        time.sleep(3)
        driver.quit()