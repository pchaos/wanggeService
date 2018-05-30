# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : hsgtcg.py

Description : 沪深港通持股

@Author :       pchaos

date：          2018-5-30
-------------------------------------------------
Change Activity:
               2018-5-30:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.db import models

class HSGTCG(models.Model):
    """ 沪深港通持股
    附注:

    1、基础数据来自港交所披露，数据展示港交所中央结算系统参与者于该日日终的持股量。如果所选择的持股日期是星期日或香港公共假期，则会显示最后一个非星期日或香港公共假期的持股记录。

    2、沪股通持股和深股通持股合成北向持股，港股通（沪）和港股通（深）合称南向持股。

    3、持股占A股百分比或者持股占发行股份百分比是按交易所相关上市公司的上市及交易的股总数而计算，有可能沒有包括公司实时动态变化，因此可能不是最新的。该数值只作为参考之用，使用该百分比时敬请注意。

    """

    code = models.CharField(verbose_name='代码', max_length=10, db_index=True, null=True)
    close = models.DecimalField(verbose_name='收盘价', max_digits=9, decimal_places=3, null=True)
    hvol = models.DecimalField(verbose_name='持股数量', max_digits=10, decimal_places=1, null=True)
    hamount = models.DecimalField(verbose_name='持股金额', max_digits=10, decimal_places=1, null=True)
    hpercent = models.DecimalField(verbose_name='持股数量占A股百分比', max_digits=6, decimal_places=3, null=True)
    tradedate = models.DateField(verbose_name='日期', null=True)

    @classmethod
    def getlist(cls, code=None):
        """
        返回stock_category类型列表

        :param stock_category: 证券类型
            STOCK_CATEGORY = ((10, "股票"),
                  (11, "指数"),
                  (12, "分级基金"),
                  (13, "债券"),
                  (14, "逆回购"),)
        :return: .objects.all().filter(category=stock_category)
        """
        if code:
            # 返回所有代码
            return cls.objects.all().filter(code=code)

        return cls.objects.all()

    def __str__(self):
        return '{} {} {} {}'.format(self.code, self.close, self.hvol, self.hamount)

    class Meta:
        verbose_name = '沪深港通持股'
        unique_together = (('code', 'tradedate'))