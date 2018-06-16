# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : proxylist.py

Description :

@Author :       pchaos

date：          18-6-13
-------------------------------------------------
Change Activity:
               18-6-13:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

MINPROXCOUNTS = 100  # 最少保存proxy数量

from django.db import models
from django.urls import reverse
from stocks.models import StockBase
from stocks.tools.proxy import get_proxy, delete_proxy
import requests
import random

def getHtml(url, proxy):
    retry_count = 2

    while retry_count > 0:
        try:
            html = requests.get(url, proxies={"http": "http://{}".format(proxy)}, timeout=25)
            # 使用代理访问
            if html.status_code:
                return html
            else:
                retry_count -= 1
        except Exception:
            retry_count -= 1
    # 出错5次, 删除代理池中代理
    delete_proxy(proxy)
    return None


class Proxy(StockBase):
    ip = models.GenericIPAddressField()
    port = models.SmallIntegerField('端口号')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return '{}:{}'.format(self.ip, self.port)

    class Meta:
        verbose_name = '代理'
        unique_together = (('ip', 'port'))

    @classmethod
    def importList(cls):
        url = 'https://api.ipify.org/'
        count = cls.objects.all().count()
        while count < MINPROXCOUNTS:
            proxy = get_proxy().decode('utf-8')
            ip, port = proxy.split(":")
            qs = cls.objects.filter(ip=ip, port=port).first()
            if qs:
                continue
            print('checking {}'.format(proxy))
            count = cls.objects.all().count()
            html = getHtml(url, proxy)
            if html:
                if html.status_code and len(html.content) == 14:
                    print('saving {}'.format(html.content.decode('utf-8')))
                    cls.saveProxy(proxy)
            else:
                print('deleting')
            print('total counts:{}'.format(count))

    @classmethod
    def saveProxy(cls, proxy):
        ip, port = proxy.split(":")
        cls.objects.get_or_create(ip=ip, port=port)

    @classmethod
    def getNextProxy(cls):
        """ 随机返回代理地址

        :return:
        """
        try:
            qs = cls.objects.all()
            return qs[int(random.random() * len(qs))].__str__()
        except Exception as e:
            return get_proxy().decode('utf-8')

    @classmethod
    def deleteProxy(cls, proxy):
        ip, port = proxy.split(":")
        qs = cls.objects.filter(ip=ip, port=port).first()
        if qs:
            qs.delete()

    @classmethod
    def getlist(cls):
        return cls.objects.all()

    def get_absolute_url(self):
        return reverse('proxy_form', args=[str(self.id)])