# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : rpsModelForm.py

Description :

@Author :       pchaos

date：          18-6-26
-------------------------------------------------
Change Activity:
               18-6-26:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
from django.forms import ModelForm
from django import forms
from stocks.models import RPS

class RPSModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = RPS
        fields = ('code', 'rps120', 'rps250', 'tradedate',)

class RPSForm(forms.Form):
    code = forms.CharField(label='代码', max_length=6, min_length = 0, required=False)
    rps120 = forms.IntegerField(label='120日RPS', max_value=100, min_value=0, required=False)
    rps250 = forms.IntegerField(label='250日RPS', max_value=100, min_value=0, required=False)


