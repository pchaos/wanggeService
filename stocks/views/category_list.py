# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : category_list.py

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

from django.shortcuts import render
from django.views.generic.list import ListView
import datetime
from stocks.models import Category, Product
from stocks.forms import CategoryForm

class CategoryListView(ListView):
    template_name = 'category_list.html'
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.datetime.now()
        context['category_form'] = CategoryForm()
        context['products'] = Product.objects.all()
        return context
