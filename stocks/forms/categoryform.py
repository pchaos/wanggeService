# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : categoryform.py

Description :

@Author :       pchaos

date：          18-7-3
-------------------------------------------------
Change Activity:
               18-7-3:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django import forms
from mptt.forms import TreeNodeChoiceField

from ..models import Category

class CategoryForm(forms.Form):
    category_model = forms.ModelChoiceField(queryset=Category.objects.all())
    category_mptt = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator='>')
