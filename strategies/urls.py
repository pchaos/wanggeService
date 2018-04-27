# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : urls.py

Description :

@Author :       pchaos

date：          2018-4-27
-------------------------------------------------
Change Activity:
               2018-4-27:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
from django.conf.urls import url
from . import views

app_name = 'strategies'

urlpatterns = [
    # ex: /strategies/
    url(r'^$', views.IndexView.as_view(), name='index'),
    # ex: /strategies/5/
    url(r'^(?P<strategy_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /strategies/5/results/
    # url(r'^(?P<strategy_id>[0-9]+)/results/$', views.results, name='results'),
]