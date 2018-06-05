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
from stocks.models import qa

__author__ = 'pchaos'


class Block(models.Model):
    """
    板块
    最上层的板块为：通达信 同花顺 自定义
    """
    code = models.CharField(verbose_name='编码', default='', max_length=18, db_index=True)
    name = models.CharField(verbose_name='板块名称', max_length=60, blank=True)
    parentblock = models.ForeignKey('self', verbose_name='上级板块', blank=True, null=True, on_delete=models.CASCADE)
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

    @classmethod
    def importTDXList(cls):
        """ 导入通达信版块
        导入通达信版块及版块明细

        :return: 通达信版块第一层
        """
        bkname = '通达信'
        bk = Block.objects.all().filter(name=bkname, parentblock=None)
        if len(bk) == 1:
            # 数据库中有通达信版块
            # data = qa.QAFetch.QATdx.QA_fetch_get_stock_block()
            data = qa.QA_fetch_stock_block_adv().data
            datatypeset = set(data.type)
            for v in datatypeset:
                # 保存版块类型
                cls(code=v, name=v, parentblock=bk[0]).save()

            querysetlist = []
            try:
                for v in datatypeset:
                    # 保存版块名称
                    # if v == 'zs':
                    #     # todo 指数版块忽略 需要处理
                    #     continue
                    bl = cls.getlist().filter(name=v)
                    if len(bl) == 1:

                        blockdf = data[data.type == v].blockname
                        blockset = set(blockdf)
                        for m in blockset:
                            block, _ = cls.objects.get_or_create(code=m, name=m, parentblock=bl[0])
                            bdetail = blockdf.reset_index()[blockdf.reset_index().blockname == m].code
                            for d in bdetail:
                                # 版块明细
                                # try:
                                    code = Listing.getlist('stock').filter(code=d)
                                    if len(code) == 0:
                                        # 不属于股票，则跳过
                                        continue
                                    querysetlist.append(BlockDetail(code=code[0], blockname=block))
                                # except Exception as e:

                        print(querysetlist)
                # bulk_create放在循环里面会报错
                BlockDetail.objects.bulk_create(querysetlist)

            except Exception as e:
                print('{}\n{} 版块： {} 版块类型： {}'.format(e.args, code, d, bl[0]))
                raise Exception
        else:
            # 初始化版块
            cls.initBlock()
            return cls.importTDXList()
        return cls.getlist(bk[0])

    @classmethod
    def getlist(cls, upperblock=None):
        if upperblock:
            return cls.objects.all().filter(parentblock=upperblock)
        else:
            return cls.objects.all()

    def __str__(self):
        return '{} - {} - {}'.format(self.parentblock, self.code, self.name)

    class Meta:
        verbose_name = '板块'
        unique_together = (('name', 'parentblock'))


class BlockDetail(models.Model):
    """
    自选股
    """
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
    blockname = models.ForeignKey(Block, on_delete=models.PROTECT)
    remark = models.CharField(verbose_name='备注', max_length=250, default='')
    isactived = models.BooleanField("有效", default=True, choices=YES_NO)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @classmethod
    def getlist(cls, upperblock=None):
        if upperblock:
            return cls.objects.all().filter(blockname=upperblock)
        else:
            return cls.objects.all()

    def __str__(self):
        return '{0} - {1}'.format(self.code, self.blockname)

    class Meta:
        # app_label ='版块明细'
        verbose_name = '版块明细'
        unique_together = (('code', 'blockname'))
