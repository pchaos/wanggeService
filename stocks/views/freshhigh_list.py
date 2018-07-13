# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : freshhigh_list.py

Description :

@Author :       pchaos

date：          18-7-11
-------------------------------------------------
Change Activity:
               18-7-11:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.views import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render
import django_filters
import datetime
from stocks.models import FreshHigh


class FreshHighFilter(django_filters.FilterSet):
    code__code = django_filters.CharFilter(label='股票代码（模糊查询）', lookup_expr='icontains')
    code__name = django_filters.CharFilter(label='股票名称（模糊查询）', lookup_expr='icontains')

    class Meta:
        model = FreshHigh
        fields = {'htradedate': ['lt', 'gt'],
                  'ltradedate': ['lt', 'gt']}


class FreshHighSearchListView(generic.ListView):
    """ 创新高后的跌幅

    """
    model = FreshHigh
    paginate_by = 150  # if pagination is desired
    template_name = 'stocks/freshhigh_search_list_grid.html'
    f = None

    def get_queryset(self):
        self.f = FreshHighFilter(self.request.GET, queryset=FreshHigh.objects.all().order_by('code'))
        # print('FreshHighFilter:{}'.format(self.f.qs))
        return self.f.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "创新高后调整幅度列表 {}".format(str(datetime.datetime.now())[:19])
        context['trueurl'] = self.request.get_raw_uri()
        context['yourip'] = self.get_IP()
        context['filter'] = self.f
        print(context['yourip'])
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
