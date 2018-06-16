# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : blockform.py

Description :

@Author :       pchaos

date：          18-6-15
-------------------------------------------------
Change Activity:
               18-6-15:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django import forms

from stocks.models import Block

__author__ = 'pchaos'


class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        exclude = ('id')