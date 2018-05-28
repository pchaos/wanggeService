# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : bk.py

Description :  版块

@Author :       pchaos

date：          2018-5-27
-------------------------------------------------
Change Activity:
               2018-5-27:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.db import models

from stocks.models import Listing, YES_NO

__author__ = 'pchaos'


class Block(models.Model):
    """
    板块
    最上层的板块为：通达信 同花顺 自定义
    """
    code = models.CharField(verbose_name='编码', default='', max_length=18, db_index=True)
    name = models.CharField(verbose_name='板块名称', max_length=60, blank=True, unique=True)
    parent = models.ForeignKey('self', verbose_name='上级板块', blank=True, null=True, on_delete=models.CASCADE)
    value1 = models.CharField(verbose_name='预留1', default='', max_length=50)
    value2 = models.CharField(verbose_name='预留2', default='', max_length=50)
    value3 = models.CharField(verbose_name='预留3', default='', max_length=50)
    remarks = models.CharField(verbose_name='备注', max_length=250, default='')
    isactived = models.BooleanField("有效", default=True, choices=YES_NO)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @staticmethod
    def initBlock():
        """
        初始化板块顶藏；
        如果板块为空，则插入顶层板块
            bklist = [['自定义', '自定义板块'],
              ['通达信', '通达信板块'],
              ['同花顺', '同花顺板块'],
              ['其他', '其他板块'], ]
        :return:
        """
        bks = Block.objects.all()
        if bks.count() == 0:
            # 初始化板块
            bklist = [['自定义', '自定义板块'],
                      ['通达信', '通达信板块'],
                      ['同花顺', '同花顺板块'],
                      ['其他', '其他板块'], ]
            i = 0
            for b in bklist:
                bk = Block(code=str(i), name=b[0], remarks=b[1])
                bk.save()
                i += 1

    def __str__(self):
        return '{} - {} - {}'.format(self.parent, self.code, self.name)
    #
    # class Meta:
    #     verbose_name = '板块'
    #     unique_together = (('name', 'parent'))

class BlockDetail(models.Model):
    """
    自选股
    """
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
    bkname = models.ForeignKey(Block, on_delete=models.PROTECT)
    remark = models.CharField(verbose_name='备注', max_length=250, default='')
    isactived = models.BooleanField("有效", choices=YES_NO)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '{0} - {1}'.format(self.code, self.bkname)

    # class Meta:
    #     app_label ='我的自选股'
    #     verbose_name = '版块明细'


