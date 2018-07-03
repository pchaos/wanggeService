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
from stocks.forms import BlockForm
from stocks.forms import BlockModelForm


class BlockSearchListView(generic.ListView):
    """ 条件查询RPS强度;
    基于django.forms.form

    """
    model = Block
    paginate_by = 150  # if pagination is desired
    template_name = 'stocks/block_search_list.html'
    code = ''
    name = ''
    initdata = {'code': '',
                'name': name,
                }
    form = BlockForm(initdata)

    def get_queryset(self):
        queryset = Block.getlist()
        self.form = BlockForm(self.request.GET)
        # print(self.form)
        if self.form.is_valid():
            self.code = self.form.cleaned_data['code']
            self.name = self.form.cleaned_data['name']
            print(self.form.cleaned_data)
            if self.code:
                try:
                    queryset = queryset.filter(code=Listing.getlist('stock').get(code=self.code))
                except:
                    pass
            if self.name:
                try:
                    queryset = queryset.filter(name__icontains=self.name)
                except:
                    pass

        return queryset.order_by('code', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "版块列表 查询时间：{}".format(str(datetime.datetime.now())[:19])
        context['code'] = self.code
        context['form'] = self.form
        context['trueurl'] = self.request.get_raw_uri()
        # print('{} {}'.format(self.context_object_name, self.form))
        return context
