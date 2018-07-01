# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : block_list.py

Description :

@Author :       pchaos

date：          18-6-29
-------------------------------------------------
Change Activity:
               18-6-29:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'
from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render
import datetime
from stocks.models import Listing
from stocks.models import Block
from stocks.forms import BlockModelForm


class RPSSearchListView(generic.ListView):
    """ 条件查询RPS强度;
    基于django.forms.form

    """
    model = Block
    paginate_by = 150  # if pagination is desired
    template_name = 'stocks/block_search_list.html'
    code=''
    name = ''
    rps250 = None
    days = 10
    page = 1
    initdata = {'code': '',
            'name': name,
            }
    form = BlockModelForm(initdata)

    def get_queryset(self):
        queryset = Block.getlist('stock')
        self.form = BlockModelForm(self.request.GET)
        # print(self.form)
        if self.form.is_valid():
            self.code = self.form.cleaned_data['code']
            self.rps120 = self.form.cleaned_data['rps120']
            self.rps250 = self.form.cleaned_data['rps250']
            # todo form choice 赋值
            # self.days = int(form.cleaned_data['days'])
            try:
                self.page = int(self.form.cleaned_data['page'])
                print('page:{}'.format(self.page))
            except:
                print('exception page:{}'.format(self.page))
                print('self.form.cleaned_data:{}'.format(self.form.cleaned_data['page']))
                # self.page = 1
                pass
            print(self.form.cleaned_data)
            if self.code:
                try:
                    queryset = queryset.filter(code=Listing.getlist('stock').get(code=self.code))
                except:
                     pass
            if self.rps120:
                try:
                    queryset = queryset.filter(rps120__gte=self.rps120)
                except:
                     pass
            if self.rps250:
                try:
                    queryset = queryset.filter(rps250__gte=self.rps250)
                except:
                     pass
            if self.days > 0:
                try:
                    tdate = Block.getNearestTradedate(days=-self.days)
                    queryset = queryset.filter(tradedate__gte=tdate)
                except:
                     pass

        return queryset.order_by('-tradedate', '-rps250', '-rps120')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "RPS强度列表 {}".format(str(datetime.datetime.now())[:19])
        context['code'] = self.code
        context['form'] = self.form
        context['trueurl'] = self.request.get_raw_uri()
        # print('{} {}'.format(self.context_object_name, self.form))
        return context
