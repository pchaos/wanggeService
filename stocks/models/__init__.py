from django.db import models
from django.utils import timezone
import datetime
import pandas as pd
import numpy as np
import QUANTAXIS as qa  # since quantaxis Version 1.0.33    2018 05 18

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


class stockABS(models.Model):
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
                    Listing(code=a.name, name=a['name'],
                            timeToMarket=datetime.datetime(d // 10000, d // 100 % 100, d % 100),
                            category=category, market=market))
            cls.objects.bulk_create(querysetlist)
        except Exception as e:
            print(e.args)
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


class RPSBase(stockABS):
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
    rps120 = models.DecimalField(verbose_name='RPS120', max_digits=7, decimal_places=3, null=True)
    rps250 = models.DecimalField(verbose_name='RPS250', max_digits=7, decimal_places=3, null=True)
    tradedate = models.DateField(verbose_name='交易日期')

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

        return cls.objects.all().filter(code__category=category)

    def __str__(self):
        return '{} {} {} {}'.format(self.code, self.rps120, self.rps250, self.tradedate)

    @staticmethod
    def count_timedelta(delta, step, seconds_in_interval):
        """Helper function for iterate.  Finds the number of intervals in the timedelta."""
        return int(delta.total_seconds() / (seconds_in_interval * step))

    @staticmethod
    def daterange(start_date, end_date):
        """ Iterating through a range of dates
        例子：
        start_date = date(2013, 1, 1)
        end_date = date(2015, 6, 2)
        for single_date in daterange(start_date, end_date):
            print(single_date.strftime("%Y-%m-%d"))

        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 从start到end截止的日期序列
        """

        from datetime import timedelta
        for n in range(int((convertToDate(end_date) - convertToDate(start_date) + 1).days)):
            yield start_date + timedelta(n)

    class Meta:
        abstract = True


class RPSprepare(RPSBase):
    """欧奈尔PRS预计算"""

    class Meta:
        # app_label ='rps计算中间量'
        verbose_name = 'RPS准备'
        unique_together = (('code', 'tradedate'))

    @classmethod
    def importIndexListing(cls):
        """
        插入所有股票指数
        :return:
        """
        codelist = Listing.getlist('index')
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = []  # quantaxis中无数据list
            for v in codelist.values():
                print('dealing: {}'.format(v))
                # get stockcode
                code = Listing.objects.get(code=v['code'], category=11)
                # 本地获取指数日线数据
                data = qa.QA_fetch_index_day_adv(v['code'], '1990-01-01', datetime.datetime.now().strftime("%Y-%m-%d"))
                if len(data) > 120:
                    df = pd.DataFrame(data.close)
                    df['rps120'] = df.close / df.close.shift(120)
                    df['rps250'] = df.close / df.close.shift(250)
                    del df['close']
                    df = df[120:]
                    for d, _, a, b in df.reset_index().values:
                        # 下面两行代码，合并写在一行，会造成tradedate错误
                        r = RPSprepare(code=code, rps120=a, rps250=b if b > 0 else None,
                                       tradedate=d.to_pydatetime())
                        querysetlist.append(r)
                else:
                    # quantaxis中无数据
                    delisted.append(a)
            print('delisted count {} :\n {}'.format(len(delisted), delisted))
            RPSprepare.objects.bulk_create(querysetlist)
        except Exception as e:
            print(e.args)
        return cls.getlist('index')


class RPS(RPSBase):
    """欧奈尔PRS"""

    @staticmethod
    def caculateRPS(df, nlist=[120, 250]):
        """ 计算n日rps

        :param df: dataframe
        :param nlist: n日list
        :return:
        """
        orgincolumns = [c for c in df.columns]
        assert len(df) > 0, 'df必须不为空'
        dfd = df
        for n in nlist:
            dfd.reset_index(inplace=True)
            rpsname = 'rps{}'.format(str(n))
            rpsn = dfd[[rpsname, 'code_id']].sort_values(by=[rpsname])
            rpsn.reset_index(inplace=True)
            rpsn['a'] = np.round(100 * (rpsn.index - rpsn.index.min()) / (rpsn.index.max() - rpsn.index.min()), 2)
            rpsn.set_index('code_id', inplace=True)
            dfd.set_index('code_id', inplace=True)
            if (rpsname not in list(dfd.columns)):
                # 结果集中没有rpsname列名，则增加空列
                dfd[rpsname] = pd.np.nan
            dfd.loc[:, (rpsname)] = rpsn['a']
        dfd.reset_index(inplace=True)
        # dfd.set_index('tradedate', inplace=True)
        return dfd[orgincolumns]

    @classmethod
    def importIndexListing(cls, start='2006-1-1', end=None):
        """
        插入所有股票指数
        :return:
        """
        if end is None:
            #  获取当天
            end = datetime.datetime.now().date()
        qs = RPSprepare.getlist('index')
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = []  # quantaxis中无数据时，保存到delisted
            for v in stocktradedate.get_real_datelisting(start, end).values('tradedate'):
                print(v)
                # 获取 v['tradedate']对应的指数列表
                qsday = qs.filter(tradedate=v['tradedate'])
                df = pd.DataFrame(list(qsday.values()))
                data = RPS.caculateRPS(df)
                aaa
                # code = Listing.objects.get(code=v.code.code, category=11)
                if len(data) > 0:
                    df = pd.DataFrame(data.close)
                    df['rps120'] = df.close / df.close.shift(120)
                    df['rps250'] = df.close / df.close.shift(250)
                    del df['close']
                    df = df[120:]
                    for a, b in df.values:
                        querysetlist.append(
                            RPS(code=code, rps120=b, rps250=b))

                else:
                    # quantaxis中无数据
                    delisted.append(a)
            print('delisted count {} :\n {}'.format(len(delisted), delisted))
            RPSprepare.objects.bulk_create(querysetlist)
        except Exception as e:
            print(e.args)
        return cls.getlist('index')

    class Meta:
        # app_label ='rps计算'
        verbose_name = '欧奈尔PRS'
        # unique_together = (('code', 'tradedate'))


class stocktradedate(models.Model):
    tradedate = models.DateField(verbose_name='交易日期', unique=True)

    @classmethod
    def getlist(cls, start=None, end=None):
        """

        """
        # 返回所有代码
        if start is None and end is None:
            return cls.objects.all()
        else:
            if start is None:
                start = datetime.datetime(1990, 1, 1)
            if end is None:
                end = datetime.datetime.now().date()
            return cls.objects.all().filter(tradedate__gte=start, tradedate__lte=end)

    @classmethod
    def importList(cls):
        """
        从qa.QAUtil.QADate_trade.trade_date_sse导入交易日期
        :return: 返回 .objects.all()
        """
        data = qa.QAUtil.QADate_trade.trade_date_sse
        if len(data) > cls.getlist().count():
            querysetlist = []
            for v in [d.date() for d in pd.to_datetime(data)]:
                querysetlist.append(stocktradedate(tradedate=v))
            cls.objects.bulk_create(querysetlist)
        return cls.getlist()

    def __str__(self):
        return '{}'.format(self.tradedate.strftime('%Y-%m-%d'))

    @classmethod
    def getlist(cls):
        """

        """
        # 返回所有代码
        return cls.objects.all()

    @classmethod
    def get_real_date(cls, date, towards=-1):
        """
        获取真实的交易日期,其中,第三个参数towards是表示向前/向后推
        towards=1 日期向后迭代
        towards=-1 日期向前迭代
        @ yutiansut

        """
        while not cls.if_tradeday(date):
            date = str(datetime.datetime.strptime(
                str(date)[0:10], '%Y-%m-%d') + datetime.timedelta(days=towards))[0:10]
        else:
            return datetime.datetime.strptime(str(date)[0:10], '%Y-%m-%d')

    @property
    def trade_date_sse(self):
        try:
            return self.tradedatelist
        except Exception as e:
            self.tradedatelist = stocktradedate.getlist().filter(tradedate__lte=datetime.datetime.now().date()).values()
            # stocktradedate.objects.values_list('tradedate').filter(tradedate__lte=datetime.datetime.now().date())
            return self.tradedatelist

    @trade_date_sse.setter
    def trade_date_sse(self, value):
        pass

    @classmethod
    def if_tradeday(cls, day):
        '日期是否交易'
        try:
            _sd = stocktradedate()
            _sd.trade_date_sse.get(tradedate=(str(day)[:10]))
            _sd = None
            return True
        except Exception as e:
            return False

    @classmethod
    def nextTradeday(cls, tradeday=None, n=1):
        """ 下一交易日

        :param tradeday:
        :param n:
        :return:
        """
        return cls.date_gap(tradeday, n, 'gt')

    @classmethod
    def preTradeday(cls, tradeday=None, n=1):
        return cls.date_gap(tradeday, n, 'lt')

    @classmethod
    def date_gap(cls, date, gap, methods):
        """[summary]

        Arguments:
            date {[type]} -- [description]
            gap {[type]} -- [description]
            methods {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        try:
            datesse = cls()
            dateid = datesse.trade_date_sse.filter(tradedate=date)[0]['id']
            if methods in ['>', 'gt']:
                td = datesse.trade_date_sse.filter(id=dateid + gap)
                return td[0]['tradedate']
            elif methods in ['>=', 'gte']:
                td = datesse.trade_date_sse.filter(id=dateid + gap - 1)
                return td[0]['tradedate']
            elif methods in ['<', 'lt']:
                td = datesse.trade_date_sse.filter(id=dateid - gap)
                return td[0]['tradedate']
            elif methods in ['<=', 'lte']:
                td = datesse.trade_date_sse.filter(id=dateid - gap + 1)
                return td[0]['tradedate']
            elif methods in ['==', '=', 'eq']:
                return date

        except:
            return 'wrong date'

    @classmethod
    def get_real_datelist(cls, start, end):
        """
        取数据的真实区间,返回的时候用 start,end=stocktradedate.get_rev2ray v2ctl verifyal_datelist()
        @yutiansut
        2017/8/10

        当start end中间没有交易日 返回None, None
        @yutiansut/ 2017-12-19
        """
        alist = cls.get_real_datelisting(start, end)
        if alist.count() == 0:
            return None, None
        else:
            return (alist[0]['tradedate'], alist[len(alist) - 1]['tradedate'])

    @classmethod
    def get_real_datelisting(cls, start, end):
        """ 取数据的真实区间列表

        :param start:
        :param end:
        :return: list of datetime.date()
        """

        datesse = cls()
        return datesse.trade_date_sse.filter(tradedate__gte=convertToDate(start), tradedate__lte=convertToDate(end))

    class Meta:
        # app_label ='rps计算'
        verbose_name = 'A股交易日'

from .bk import Block
from .bk import BlockDetail
