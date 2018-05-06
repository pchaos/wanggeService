# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@File    : urls.py
Description :
@Author :       pchaos
date：          18-4-3
-------------------------------------------------
Change Activity:
               18-4-3:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import re_path
from comment.views import ArticleCommentView
from . import views

app_name = 'comment'

urlpatterns = [
    re_path(r'^$', views.ArticleCommentView.as_view(), name='article-list'),
    re_path(r'^(?P<pk>[0-9]+)/$', views.ArticleCommentView.as_view(), name='detail'),
    re_path(r'^(?P<article_id>[0-9]+)/comment/$', ArticleCommentView.as_view(), name='article_comment'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
