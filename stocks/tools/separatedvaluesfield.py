# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : separatedvaluesfield.py

Description : store a list in the Django models
    To return a list of friend names we'll need to create a custom Django Field class that will return a list when accessed.
    https://stackoverflow.com/questions/1110153/what-is-the-most-efficient-way-to-store-a-list-in-the-django-models?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

@Author :       pchaos

date：          18-5-31
-------------------------------------------------
Change Activity:
               18-5-31:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.db import models
import ast

class ListField(models.TextField):
    __metaclass__ = models.Field
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return (value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)