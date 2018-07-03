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


class BlockModelForm(forms.ModelForm):
    class Meta:
        model = Block
        exclude = ('id','value1', 'value2', 'value3', 'remarks')

class BlockForm(forms.Form):
    code = forms.CharField(label='编码', max_length=18, required=False)
    name = forms.CharField(label='板块名称', max_length=60, required=False)