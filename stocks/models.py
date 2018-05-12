from django.db import models
import django.utils.timezone

STOCK_CATEGORY = ((10, "股票"),
                  (11, "指数"),
                  (12, "分级基金"),
                  (13, "债券"),
                  (14, "逆回购"),)

YES_NO = ((True, "是"),
          (False, "否"))

MARKET_CHOICES = ((0, "深市"), (1, "沪市"))


class Stockcode(models.Model):
    code = models.CharField(verbose_name='代码', max_length=10, unique=True, db_index=True)
    name = models.CharField(verbose_name='名称', max_length=8)
    shortcut = models.CharField(verbose_name='快捷键', default='', max_length=8)
    usedName = models.CharField(verbose_name='曾用名', max_length=255, default='')
    market = models.IntegerField('市场', default=0, choices=MARKET_CHOICES)
    timeToMarket = models.DateField(verbose_name='上市日期')
    decimalpoint = models.SmallIntegerField("价格小数位数", default=2)
    volunit = models.IntegerField("每次交易最小成交单位", default=100)
    category = models.SmallIntegerField("交易类别", default=10, choices=STOCK_CATEGORY)
    isdelisted = models.SmallIntegerField("是否退市", default=False, choices=YES_NO)

    def __str__(self):
        return '{0} {1}'.format(self.code, self.name)

    # class Meta:
    #     app_label ='我的股票'
    #     verbose_name = '股票代码'
from django.utils import timezone
class StockDay(models.Model):
    code = models.ForeignKey(Stockcode, verbose_name='代码', on_delete=models.PROTECT)
    open = models.DecimalField(verbose_name='开盘价', max_digits=9, decimal_places=3, null=True)
    close = models.DecimalField(verbose_name='收盘价', max_digits=9, decimal_places=3, null=True)
    high = models.DecimalField(verbose_name='最高价', max_digits=9, decimal_places=3, null=True)
    low = models.DecimalField(verbose_name='最低价', max_digits=9, decimal_places=3, null=True)
    volumn = models.DecimalField(verbose_name='vol', max_digits=9, decimal_places=3, null=True)
    amount = models.DecimalField(verbose_name='金额', max_digits=9, decimal_places=3, null=True)
    date = models.DateField(verbose_name='日期', db_index=True)




class BK(models.Model):
    """
    板块
    最上层的板块为：通达信 同花顺 自定义
    """
    code = models.CharField(verbose_name='编码',  default='', max_length=18, db_index=True)
    name = models.CharField(verbose_name='板块名称', max_length=60, blank=True, unique=True)
    parent = models.ForeignKey('self', verbose_name='上级板块', blank=True, null=True,  on_delete=models.CASCADE)
    value1 = models.CharField(verbose_name='预留1',  default='', max_length=50)
    value2 = models.CharField(verbose_name='预留2',  default='', max_length=50)
    value3 = models.CharField(verbose_name='预留3',  default='', max_length=50)
    remarks = models.CharField(verbose_name='备注', max_length=250, default='')
    isactived = models.BooleanField("有效", default=True, choices=YES_NO)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '{} - {} - {}'.format(self.parent, self.code, self.name)


class BKDetail(models.Model):
    """
    自选股
    """
    code = models.ForeignKey(Stockcode, verbose_name='代码', on_delete=models.PROTECT)
    bkname = models.ForeignKey(BK, on_delete=models.PROTECT)
    remark = models.CharField(verbose_name='备注', max_length=250, default='')
    isactived = models.BooleanField("有效", choices=YES_NO)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '{0} - {1}'.format(self.code, self.bkname)

    # class Meta:
    #     app_label ='我的自选股'
    #     verbose_name = '自选股'
