# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : forms.py.py

Description :

@Author :       pchaos

date：          2018-4-22
-------------------------------------------------
Change Activity:
               2018-4-22:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.forms import ModelForm, HiddenInput
from .models import ArticleComment, ArticleCommentReply

class ArticleCommentForm(ModelForm):
    class Meta:
        model = ArticleComment
        fields = ['content', 'article']
        widgets = {
            'article': HiddenInput,
        }

class ArticleCommentReplyForm(ModelForm):
    class Meta:
        model = ArticleCommentReply
        fields = ['content', 'comment', 'reply']
        widgets = {
            'comment': HiddenInput,
            'reply': HiddenInput,
        }

