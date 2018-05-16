# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : forms.py

Description :

@Author :       pchaos

tradedate：          2018-4-21
-------------------------------------------------
Change Activity:
               2018-4-21:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django import forms
from stocks.models import BK

class BKForm(forms.ModelForm):
    class Meta:
        model = BK
        exclude = ('id')
