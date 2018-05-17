from django.db import models
from django.utils import timezone
from datetime import datetime
import pandas as pd

STOCK_CATEGORY = ((10, "股票"),
                  (11, "指数"),
                  (12, "分级基金"),
                  (13, "债券"),
                  (14, "逆回购"),)

YES_NO = ((True, "是"),
          (False, "否"))

MARKET_CHOICES = ((0, "深市"), (1, "沪市"))

class stockABS(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def getCategory(cls, type_='stock'):
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
        return category


class Listing(stockABS):
    code = models.CharField(verbose_name='代码', max_length=10, db_index=True)
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
                    Listing(code=a.name, name=a['name'], timeToMarket=datetime(d // 10000, d // 100 % 100, d % 100),
                            category=category, market=market))
            self.objects.bulk_create(querysetlist)
        except Exception as e:
            print(e.args)
        return df

    @classmethod
    def importIndexListing(self):
        """
        插入所有股票指数
        :return:
        """
        import QUANTAXIS as qa
        df = qa.QAFetch.QATdx.QA_fetch_get_stock_list('index')
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = [] # quantaxis中无数据list
            for i in df.index:
                print(i)
                a = df.loc[i]
                # 本地获取指数日线数据
                data = qa.QA_fetch_index_day_adv(a.code, '1990-01-01', timezone.now().strftime("%Y-%m-%d"))
                if len(data) > 0:
                    d = data.data.date[0].strftime("%Y-%m-%d")  # 起始交易日期 上市日期
                    if a.sse == 'sh':
                        market = 1
                    else:
                        market = 0
                    category = 11
                    querysetlist.append(
                        Listing(code=a.code, name=a['name'], timeToMarket=d, volunit=a.volunit,
                                decimalpoint=a.decimal_point,
                                category=category, market=market))

                else:
                    # quantaxis中无数据
                    delisted.append(a)
                    isdelisted = True
            # print('delisted count {} :\n {}'.format(len(delisted), delisted))
            self.objects.bulk_create(querysetlist)
        except Exception as e:
            print(a, e.args)
        return self.getCodelist('index')

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
        :return: .objects.all().filter(category=stock_category)
        """
        if type_ in ['ALL', 'all']:
            # 返回所有代码
            return self.objects.all()

        category = self.getCategory(type_)

        return self.objects.all().filter(category=category)

    class Meta:
        # app_label ='证券列表'
        verbose_name = '证券列表'
        unique_together = (('code', 'market', 'category'))


class StockDay(models.Model):
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
    open = models.DecimalField(verbose_name='开盘价', max_digits=9, decimal_places=3, null=True)
    close = models.DecimalField(verbose_name='收盘价', max_digits=9, decimal_places=3, null=True)
    high = models.DecimalField(verbose_name='最高价', max_digits=9, decimal_places=3, null=True)
    low = models.DecimalField(verbose_name='最低价', max_digits=9, decimal_places=3, null=True)
    volumn = models.DecimalField(verbose_name='vol', max_digits=9, decimal_places=3, null=True)
    amount = models.DecimalField(verbose_name='金额', max_digits=9, decimal_places=3, null=True)
    tradedate = models.DateField(verbose_name='日期', db_index=True)


    class Meta:
        verbose_name = '日数据'
        unique_together = (('code', 'tradedate'))

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
    #
    # class Meta:
    #     verbose_name = '板块'
    #     unique_together = (('name', 'parent'))


class BKDetail(models.Model):
    """
    自选股
    """
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
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
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
    bkname = models.ForeignKey(BK, on_delete=models.PROTECT)
    rps120 = models.DecimalField(verbose_name='RPS120', max_digits=7, decimal_places=3, null=True)
    rps250 = models.DecimalField(verbose_name='RPS250', max_digits=7, decimal_places=3, null=True)
    tradedate = models.DateTimeField(verbose_name='交易日期', auto_now_add=True)

    class Meta:
        # app_label ='rps计算'
        verbose_name = 'RPS'
        unique_together = (('code', 'tradedate'))

class RPSprepare(stockABS):
    """欧奈尔PRS预计算"""
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
    rps120 = models.DecimalField(verbose_name='RPS120', max_digits=7, decimal_places=3, null=True)
    rps250 = models.DecimalField(verbose_name='RPS250', max_digits=7, decimal_places=3, null=True)
    tradedate = models.DateTimeField(verbose_name='交易日期', auto_now_add=True)

    class Meta:
        # app_label ='rps计算中间量'
        verbose_name = 'RPS准备'
        unique_together = (('code', 'tradedate'))

    @classmethod
    def importIndexListing(self):
        """
        插入所有股票指数
        :return:
        """
        import QUANTAXIS as qa
        codelist = Listing.getCodelist('index')
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = [] # quantaxis中无数据list
            for v in codelist.values():
                print(v)
                # get stockcode
                code = Listing.objects.get(code=v['code'], category=11)
                # 本地获取指数日线数据
                data = qa.QA_fetch_index_day_adv(v['code'], '1990-01-01', timezone.now().strftime("%Y-%m-%d"))
                if len(data) > 120:
                    df = pd.DataFrame(data.close)
                    df['rps120'] = df.close / df.close.shift(120)
                    df['rps250'] = df.close / df.close.shift(250)
                    del df['close']
                    df = df[120:]
                    for a,b in df.values:
                        querysetlist.append(
                            RPSprepare(code=code, rps120=a, rps250=b if b > 0 else None))

                else:
                    # quantaxis中无数据
                    delisted.append(a)
            print('delisted count {} :\n {}'.format(len(delisted), delisted))
            RPSprepare.objects.bulk_create(querysetlist)
        except Exception as e:
            print(e.args)
        return self.getCodelist('index')

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
        :return: .objects.all().filter(category=stock_category)
        """
        if type_ in ['ALL', 'all']:
            # 返回所有代码
            return self.objects.all()

        category = self.getCategory(type_)

        return self.objects.all().filter(code__category=category)

# from django.conf import settings
# if not settings.TESTING:
#     # 非测试环境,自动插入股票代码
#     from django import db
#     import os
#     db_name = db.utils.settings.DATABASES['default']['NAME']
#     if os.path.isfile(db_name):
#         # from . import Listing
#         if Listing.getCodelist().count() == 0:
#             print('importing stock listing ...')
#             Listing.importStockListing()
#         if Listing.getCodelist('index') == 0:
#             print('importing index listing ...')
#             Listing.importIndexListing()
