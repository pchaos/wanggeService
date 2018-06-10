from django.db import models
from django.utils import timezone
import datetime
import pandas as pd
import QUANTAXIS as qa  # since quantaxis Version 1.0.33    2018 05 18
from .base import StockBase

STOCK_CATEGORY = ((10, "股票"),
                  (11, "指数"),
                  (12, "分级基金"),
                  (13, "债券"),
                  (14, "逆回购"),)

YES_NO = ((True, "是"),
          (False, "否"))

MARKET_CHOICES = ((0, "深市"), (1, "沪市"))

# 例如： 2017-01-01
DATE_FORMAT = '%Y-%m-%d'


def convertToDate(date, dateformat=DATE_FORMAT):
    """ 转换为日期类型

    :param date: DATE_FORMAT = '%Y-%m-%d'
    例如： '2017-01-01'

    :return:  返回日期 date.date()
    """
    try:
        date = datetime.datetime.strptime(date, dateformat)
        return date.date()
    except TypeError:
        return date


class stockABS(StockBase):
    class Meta:
        abstract = True

    @classmethod
    def getCategory(cls, type_='stock'):
        """
        类别
        支持整数类型、字符串类别
        :param type_: 可取值： 'stock', 'index', 'etf',
        :return:
        """
        if type(type_) == int:
            # type_类型为整数
            category = type_
        elif type_ in ['stock', 'gp']:
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
    isactived = models.BooleanField('是否有效', default=True)
    isdelisted = models.SmallIntegerField("是否退市", default=False, choices=YES_NO)

    def __str__(self):
        return '{0} {1}'.format(self.code, self.name)

    @classmethod
    def importStockListing(cls):
        """
        插入所有上市股票公司
        :return:
        """
        from oneilquant.ONEIL.Oneil import OneilKDZD as oneil
        oq = oneil()
        n1 = 0
        df = oq.listingDate(n1)
        # todo 如果已经插入，则判断是否有更新 调用savedf方法可以实现判断有更新
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
                    Listing(code=a.name, name=a['name'],
                            timeToMarket=datetime.datetime(d // 10000, d // 100 % 100, d % 100),
                            category=category, market=market))
            cls.objects.bulk_create(querysetlist)
        except Exception as e:
            print(e.args)
            return pd.DataFrame()
        return df

    @classmethod
    def importIndexListing(cls):
        """
        插入所有股票指数
        :return:
        """
        df = qa.QAFetch.QATdx.QA_fetch_get_stock_list('index')
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = []  # quantaxis中无数据list
            print('importing ...')
            for i in df.index:
                # print(i)
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
            cls.objects.bulk_create(querysetlist)
        except Exception as e:
            print(a, e.args)
        return cls.getlist('index')

    @classmethod
    def getlist(cls, type_='stock'):
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
            return cls.objects.all()

        category = cls.getCategory(type_)

        return cls.objects.all().filter(category=category)

    class Meta:
        # app_label ='证券列表'
        verbose_name = '证券列表'
        unique_together = (('code', 'market', 'category'))


class StockDay(StockBase):
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

from .stocktradedate import Stocktradedate
from .rps import RPS, RPSprepare
from .bk import Block
from .bk import BlockDetail
from .hsgtcg import HSGTCG, HSGTCGHold