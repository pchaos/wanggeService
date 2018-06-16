# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : proxyModelForm.py

Description :

@Author :       pchaos

date：          18-6-14
-------------------------------------------------
Change Activity:
               18-6-14:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
from django.forms import ModelForm
from stocks.models.proxylist import Proxy


class ProxylistModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProxylistModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Proxy
        fields = ('ip', 'port',)

