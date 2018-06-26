# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : rps_list.py

Description :

@Author :       pchaos

date：          18-6-24
-------------------------------------------------
Change Activity:
               18-6-24:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
from django.views import generic
import datetime
from stocks.models import RPS
from stocks.models import Listing

class RPSListView(generic.ListView):
    model = RPS
    paginate_by = 150  # if pagination is desired
    code=''

    def get_queryset(self):
        queryset = []
        queryset = RPS.getlist()
        self.code = self.request.GET.get('code', '')
        if self.code:
            try:
                queryset = RPS.getlist('stock').filter(code=Listing.getlist('stock').get(code=self.code))
            except:
                queryset = RPS.getlist('stock').filter(code=None)
        return queryset.order_by('-tradedate', '-rps250', '-rps120')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "RPS强度列表 {}".format(str(datetime.datetime.now())[:19])
        context['code'] = self.code
        return context
