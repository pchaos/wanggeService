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
from django.http import HttpResponseRedirect
from django.shortcuts import render
import datetime
from stocks.models import RPS
from stocks.models import Listing
from stocks.forms import RPSForm

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

class RPSSearchListView(generic.ListView):
    """ 条件查询RPS强度

    """
    model = RPS
    paginate_by = 150  # if pagination is desired
    template_name = 'stocks/rps_search_list.html'
    code=''
    rps120 = None
    rps250 = None
    initdata = {'code': '',
            'rps120': 80,
           'rps250':80}
    form = RPSForm(initdata)
    print(form)

    def get_queryset(self):
        queryset = RPS.getlist('stock')
        form = RPSForm(self.request.GET)
        if form.is_valid():
            self.code = form.cleaned_data['code']
            self.rps120 = form.cleaned_data['rps120']
            self.rps250 = form.cleaned_data['rps250']
            print(form.cleaned_data)
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

        return queryset.order_by('-tradedate', '-rps250', '-rps120')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "RPS强度列表 {}".format(str(datetime.datetime.now())[:19])
        context['code'] = self.code
        context['form'] = self.form
        print(self.form)
        return context


def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RPSForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RPSForm()

    return render(request, 'name.html', {'form': form})