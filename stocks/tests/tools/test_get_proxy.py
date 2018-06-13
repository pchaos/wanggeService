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

__author__ = 'pchaos'


class TestGet_proxy(TestCase):
    def test_get_proxy(self):
        proxy = get_proxy()
        self.assertTrue(len(proxy) > 10, '返回结果应大于十字节：{}'.format(proxy))
        proxyList = []
        n = 10
        for i in range(n):
            proxyList.append(get_proxy())
        self.assertTrue(len(set(proxyList)) == n, '每次返回值都应该不同：{}'.format(proxyList))

