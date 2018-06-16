# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : proxy_list.py

Description :

@Author :       pchaos

date：          18-6-15
-------------------------------------------------
Change Activity:
               18-6-15:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.views import generic
import datetime
from stocks.models import Proxy

class ProxyListView(generic.ListView):
    model = Proxy
    paginate_by = 100  # if pagination is desired
    ip=''

    def get_queryset(self):
        queryset = []
        queryset = Proxy.getlist()
        self.ip = self.request.GET.get('ip', '')
        if self.ip:
            queryset = Proxy.getlist(self.ip)
        return queryset.order_by('created_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "代理IP列表 {}".format(str(datetime.datetime.now())[:19])
        return context
