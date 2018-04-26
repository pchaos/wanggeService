# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : wanggeassets.py

Description : 资产网格管理

@Author :       pchaos

date：          2018-4-24
-------------------------------------------------
Change Activity:
               2018-4-24:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from .wangge import WangGebase

def fibe(n):
    m,a, b=1, 0,1
    while (m < n):
        a,b=b,a+b
        m +=1
    return b


class AssetsBase():
    name = 'Unknown Assets'

    def __init__(self, WangGebase):
        self._wangge = WangGebase


