# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@File    : urls.py
Description :
@Author :       pchaos
tradedate：          18-4-3
-------------------------------------------------
Change Activity:
               18-4-3:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = "stocks"

urlpatterns = [
    url(r'^stocks/stocks/$', views.stockcode_list, name='stockcodeList'),
    url(r'^stocks/stocks/(?P<pk>[0-9]+)$', views.stockcode_detail, name='stockcodeDetail'),
    url(r'^ZXG/$', views.ZXG_list, name='ZXGList'),
    url(r'^ZXG/(?P<pk>[0-9]+)$', views.ZXG_detail, name='ZXGDetail'),
    url(r'^HSGTCGHold/$', views.HSGTCGHoldView, name='hsgtcghold_list'),
    url(r'^HSGTCG/$', views.HSGTCGListView.as_view(), name='hsgtcg_list'),
    url(r'^HSGTCG/(?P<pk>[0-9]+)$', views.HSGTCGHoldView, name='hsgtcgDetail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
