# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_tags.py

Description :

@Author :       pchaos

date：          18-7-13
-------------------------------------------------
Change Activity:
               18-7-13:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from unittest import TestCase
from stocks.templatetags.tags import *
__author__ = 'pchaos'


class TestChangePage(TestCase):
    def test_changePage(self):
        pg = 'page='
        url = 'http://127.0.0.1:8000/v1/HIGH/?page='
        page =3
        s = changePage(url+ str(page), page)
        result = url + str(page)
        self.assertTrue(s == result, '{} ！= {}'.format(s, result))

        page = None
        url ='http://127.0.0.1:8000/v1/HIGH/'
        s = changePage(url, page)
        result = url
        self.assertTrue(s == result, '{} ！= {}'.format(s, result))

        page = 10
        url ='http://127.0.0.1:8000/v1/HIGH/'
        s = changePage(url, page)
        result = url + '?{}'.format(pg) + str(page)
        self.assertTrue(s == result, '{} ！= {}'.format(s, result))

