# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : proxyview.py

Description :

@Author :       pchaos

date：          2018-6-15
-------------------------------------------------
Change Activity:
               2018-6-15:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from stocks.forms import ProxylistModelForm
from stocks.models import Proxy


def get_proxy_name(request, pk):
    # 如果form通过POST方法发送数据
    if request.method == 'POST':
        # 接受request.POST参数构造form类的实例
        a = Proxy.objects.get(pk=1)
        form = ProxylistModelForm(request.POST, instance=a)
        # 验证数据是否合法
        if form.is_valid():
            # 处理form.cleaned_data中的数据
            # form.save()
            # 重定向到一个新的URL
            return HttpResponseRedirect('/thanks/')

    # 如果是通过GET方法请求数据，返回一个空的表单
    else:
        form = ProxylistModelForm()

    return render(request, 'stocks/proxyform.html', {'form': form})

class ProxyDetailView(generic.DetailView):
    model = Proxy

class ProxyUpdate(UpdateView):
    model = Proxy
    fields = ('ip', 'port',)

class ProxyDelete(DeleteView):
    model = Proxy
    success_url = reverse_lazy('proxy-list')