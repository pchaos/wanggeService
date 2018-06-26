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
from .views import HSGTCGListView, HSGTCGHoldView
from .views import ZXG_list, ZXG_detail, stockcode_list, stockcode_detail
from .views import get_proxy_name
from .views import ProxyListView, ProxyDetailView
from .views import ProxyUpdate
from .views import RPSListView

app_name = "stocks"

urlpatterns = [
    url(r'^stocks/stocks/$', stockcode_list, name='stockcodeList'),
    url(r'^stocks/stocks/(?P<pk>[0-9]+)$', stockcode_detail, name='stockcodeDetail'),
    url(r'^ZXG/$', ZXG_list, name='ZXGList'),
    url(r'^ZXG/(?P<pk>[0-9]+)$', ZXG_detail, name='ZXGDetail'),
    url(r'^HSGTCGHold/$', HSGTCGHoldView, name='hsgtcghold_list'),
    url(r'^HSGTCG/$', HSGTCGListView.as_view(), name='hsgtcg_list'),
    url(r'^HSGTCG/(?P<code>[0-9]+)$', HSGTCGListView.as_view(), name='hsgtcg_list_code'),
    url(r'^HSGTCG/(?P<pk>[0-9]+)$', HSGTCGHoldView, name='hsgtcgDetail'),

    url(r'^PROXY/$', ProxyListView.as_view(), name='proxy_list'),
    url(r'^PROXY/([0-9]+)$', ProxyUpdate.as_view(), name='proxy_update'),
    url(r'^PROXYDETAIL/([0-9]+)$', ProxyDetailView.as_view(), name='proxy_form'),
    url(r'^rps/$', RPSListView.as_view(), name='rps_list'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
