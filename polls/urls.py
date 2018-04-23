# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : urls.py.py

Description :

@Author :       pchaos

date：          18-4-22
-------------------------------------------------
Change Activity:
               18-4-22:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.conf.urls import url
from . import views

app_name = 'polls'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]