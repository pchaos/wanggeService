from django.db import models
import django.utils.timezone

YES_NO = ((False, "否"),
          (True, "是"))

MARKET_CHOICES = ((0, "深市"), (1, "沪市"))


class Stockcode(models.Model):
    code = models.CharField(verbose_name='代码', max_length=10, unique=True, db_index=True)
    name = models.CharField(verbose_name='名称', max_length=8)
    usedName = models.CharField(verbose_name='曾用名', max_length=255, default='')
    market = models.IntegerField('市场', default=0, choices=MARKET_CHOICES)
    update = models.DateField(verbose_name='上市日期')
    isindex = models.SmallIntegerField("是否指数", default=False, choices=YES_NO)
    isdelisted = models.SmallIntegerField("是否退市", default=False, choices=YES_NO)

    def __str__(self):
        return '{0} {1}'.format(self.code, self.name)

    # class Meta:
    #     app_label ='我的股票'
    #     verbose_name = '股票代码'


class BK(models.Model):
    """
    板块
    """
    name = models.CharField(verbose_name='板块名称', max_length=60, blank=True, unique=True)
    parent = models.ForeignKey('self', verbose_name='上级板块', blank=True, null=True,  on_delete=models.CASCADE)
    remark = models.CharField(verbose_name='备注', max_length=250, default='')
    isactived = models.BooleanField("有效", choices=YES_NO)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')


class ZXG(models.Model):
    """
    自选股
    """
    code = models.ForeignKey(Stockcode, on_delete=models.PROTECT)
    bkname = models.ForeignKey(BK, on_delete=models.PROTECT)
    remark = models.CharField(verbose_name='备注', max_length=250, default='')
    isactived = models.BooleanField("有效", choices=YES_NO)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # class Meta:
    #     app_label ='我的自选股'
    #     verbose_name = '自选股'
