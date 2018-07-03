# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : productcategory.py

Description :

@Author :       pchaos

date：          18-7-3
-------------------------------------------------
Change Activity:
               18-7-3:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from decimal import Decimal
from django.utils.translation import ugettext_lazy as _

class Category(MPTTModel):
    name = models.CharField('名称', max_length=100, blank=False, unique=True)
    description = models.TextField('详细描述', blank=True, null=True)

    parent = TreeForeignKey('self', verbose_name='上级类别', null=True, blank=True, related_name='children', on_delete=models.CASCADE, db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = verbose_name_plural = "类别"

    def __str__(self):              # __unicode__ on Python 2
        return self.name


class Product(models.Model):
    code = models.CharField('代码', max_length=50, primary_key=True)
    name = models.CharField('名称', max_length=100, blank=True)
    category = TreeForeignKey('Category', verbose_name='类别', null=True, blank=True, on_delete=models.CASCADE, db_index=True)
    # image = models.ImageField(upload_to='foto', height_field=None, width_field=None, max_length=100, blank=True, null=True)
    description = models.TextField('详细描述', blank=True, null=True)
    stocks = models.IntegerField('是否交易', default=0, blank=True)

    #PRICES
    priceAustria = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'), verbose_name="推荐价格", blank=True, null=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    # def image_img(self):
    #     if self.image:
    #         return u'<img src="%s" width="75" height="75" />' % (self.image.url)
    #     else:
    #         return '(No image)'
    # image_img.short_description = 'Image'
    # image_img.allow_tags = True

    class Meta:
        verbose_name = verbose_name_plural = "商品"