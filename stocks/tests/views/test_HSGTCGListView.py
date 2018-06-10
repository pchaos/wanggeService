# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_HSGTCGListView.py

Description :

@Author :       pchaos

date：          18-6-9
-------------------------------------------------
Change Activity:
               18-6-9:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from django.test import Client
# from django.core.urlresolvers import rev    e

__author__ = 'pchaos'


class TestHSGTCGListView(TestCase):
    def test_get_context_data(self):
        response = self.client.get('/')
        self.assertTrue(response.status_code == '200')
        # response = self.client.get(reverse('blog_index'))
