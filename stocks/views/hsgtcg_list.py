# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : hsgtcg_list.py

Description :

@Author :       pchaos

date：          18-6-3
-------------------------------------------------
Change Activity:
               18-6-3:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.views import generic
import datetime
from stocks.models import HSGTCG
from stocks.models import Listing

class HSGTCGListView(generic.ListView):
    model = HSGTCG
    paginate_by = 100  # if pagination is desired
    code=''

    def get(self, request, *args, **kwargs):
        self.code = request.GET.get('code', '' )

        return super(HSGTCGListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = []
        queryset = HSGTCG.getlist()
        self.code = self.request.GET.get('code', '')
        if self.code:
            queryset = HSGTCG.getlist(self.code).order_by('-tradedate')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "北向持股列表 {}".format(str(datetime.datetime.now())[:19])
        return context
