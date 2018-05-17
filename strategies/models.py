from django.db import models
from stocks.models import Listing


class BaseModel(models.Model):
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class StrategyType(BaseModel):
    """
    策略类型；
    分为价格策略（简单网格、等比网格）、资金策略（简单网格、等比网格）
    """
    code = models.CharField(verbose_name='编号', max_length=10, unique=True, db_index=True)
    name = models.CharField(verbose_name='名称', max_length=100)
    remark = models.CharField(verbose_name='备注', max_length=255)

    def __str__(self):
        return "{}-{}".format(self.code, self.name)


class Strategy(BaseModel):
    """
    策略；
    价格策略、资金策略与买卖方向组合形成多种策略
    """
    #
    SELL_CHOICES = ((0, "默认"), (1, "买"), (2, "卖"))
    code = models.CharField(verbose_name='编号', max_length=10, unique=True, db_index=True)
    name = models.CharField(verbose_name='名称', max_length=50)
    stockcode = models.ForeignKey(Listing, null=True, blank=True, on_delete=models.PROTECT)
    strategytype = models.ForeignKey(StrategyType, on_delete=models.PROTECT)
    sell_choices = models.SmallIntegerField('买卖方向', default=0, choices=SELL_CHOICES)
    remark = models.CharField(verbose_name='备注', max_length=255)
    deleted = models.BooleanField('已删除', default=False)

    def __str__(self):
        return "{}-{}".format(self.code, self.name)


class StrategyDetail(BaseModel):
    strategy = models.ForeignKey(Strategy, on_delete=models.PROTECT)
    orderid = models.SmallIntegerField(verbose_name='序号', null=False)
    # 设置最多允许的值： 99,999,999 ,999 .9999
    num = models.DecimalField('数量', max_digits=15, decimal_places=4, default=0)
    expressions = models.CharField('表达式', max_length=255, default='')
