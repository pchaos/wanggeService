from django.db import models
import django.utils.timezone
from datetime import datetime

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
    name = models.CharField(verbose_name='公司简称', max_length=8)
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
    #     verbose_name = '上市公司'

    @classmethod
    def importStockListing(self):
        """
        插入所有上市股票公司
        :return:
        """
        from oneilquant.ONEIL.Oneil import OneilKDZD as oneil
        oq = oneil()
        n1 = 0
        df = oq.listingDate(n1)
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            for i in df.index:
                a = df.loc[i]
                d = int(a.timeToMarket)
                if a[0] == '6':
                    market = 1
                else:
                    market = 0
                category = 10
                querysetlist.append(
                    Stockcode(code=a.name, name=a['name'], timeToMarket=datetime(d // 10000, d // 100 % 100, d % 100),
                              category=category, market=market))
            Stockcode.objects.bulk_create(querysetlist)
        except Exception as e:
            pass
        return df

    @classmethod
    def getCodelist(self, type_='stock'):
        """
        返回stock_category类型列表
        :param stock_category: 证券类型
            STOCK_CATEGORY = ((10, "股票"),
                  (11, "指数"),
                  (12, "分级基金"),
                  (13, "债券"),
                  (14, "逆回购"),)
        :return: Stockcode.objects.all().filter(category=stock_category)
        """
        if type_ in ['stock', 'gp']:
            category = 10
        elif type_ in ['index', 'zs']:
            category = 11
        elif type_ in ['etf', 'ETF']:
            category = 12
        elif type_ in ['ZAIQ', 'ZQ']:
            category = 13
        elif type_ in ['NIHUIGOU', 'NHG']:
            category = 14

        return Stockcode.objects.all().filter(category=category)


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


class RPS(models.Model):
    """欧奈尔PRS"""
    code = models.ForeignKey(Stockcode, verbose_name='代码', on_delete=models.PROTECT)
    bkname = models.ForeignKey(BK, on_delete=models.PROTECT)
    rps120 = models.DecimalField(verbose_name='RPS120', max_digits=7, decimal_places=3, null=True)
    rps250 = models.DecimalField(verbose_name='RPS250', max_digits=7, decimal_places=3, null=True)


class RPSprepare(models.Model):
    """欧奈尔PRS预计算"""
    code = models.ForeignKey(Stockcode, verbose_name='代码', on_delete=models.PROTECT)
    rps120 = models.DecimalField(verbose_name='RPS120', max_digits=7, decimal_places=3, null=True)
    rps250 = models.DecimalField(verbose_name='RPS250', max_digits=7, decimal_places=3, null=True)

    class Meta:
        # app_label ='我的自选股'
        verbose_name = 'RPS'
