# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : rps_list.py

Description :

@Author :       pchaos

date：          18-6-24
-------------------------------------------------
Change Activity:
               2018-7-2:
               add  get client's IP address

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
    """ 条件查询RPS强度;
    基于django.forms.form

    """
    model = RPS
    paginate_by = 150  # if pagination is desired
    template_name = 'stocks/rps_search_list.html'
    code=''
    rps120 = None
    rps250 = None
    days = 10
    page = 1
    column_num = 3
    initdata = {'code': '',
            'rps120': str(80),
            'rps250':str(80)
            # 'days':str(days),
            # 'page':str(page),
            # 'column_num': str(column_num)
            }
    form = RPSForm(initdata)

    def get_queryset(self):
        queryset = RPS.getlist('stock')
        self.form = RPSForm(self.request.GET)
        # print(self.form)
        if self.form.is_valid():
            self.code = self.form.cleaned_data['code']
            self.rps120 = self.form.cleaned_data['rps120']
            self.rps250 = self.form.cleaned_data['rps250']
            self.column_num = self.form.cleaned_data['column_num']
            # todo form choice 赋值
            # self.days = int(form.cleaned_data['days'])
            try:
                self.page = int(self.form.cleaned_data['page'])
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
                    tdate = RPS.getNearestTradedate(days=-self.days)
                    queryset = queryset.filter(tradedate__gte=tdate)
                except:
                     pass

        return queryset.order_by('-tradedate', '-rps250', '-rps120')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "RPS强度列表 {}".format(str(datetime.datetime.now())[:19])
        context['code'] = self.code
        if self.column_num is None:
            self.column_num = 3
        context['column_num'] = self.column_num
        print('column_num :{}'.format(self.column_num))
        context['form'] = self.form
        context['trueurl'] = self.request.get_raw_uri()
        context['yourip'] = self.get_IP()
        # print('{} {}'.format(self.context_object_name, self.form))
        return context

    def get_IP(self):
        """  get client's IP address

        :return: client ip
        """
        from ipware import get_client_ip
        client_ip, is_routable = get_client_ip(self.request)
        if client_ip is None:
            # Unable to get the client's IP address
            return 'N/A'
        else:
            # We got the client's IP address
            if is_routable:
                # The client's IP address is publicly routable on the Internet
                pass
            else:
                # The client's IP address is private
                pass
        return client_ip

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