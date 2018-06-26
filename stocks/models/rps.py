# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : rps.py

Description : 计算欧奈尔RPS

@Author :       pchaos

date：          2018-5-29
-------------------------------------------------
Change Activity:
               18-5-29:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.db import models
from django.db import transaction
from django.db.models import Max
import datetime

import QUANTAXIS as qa
import numpy as np
import pandas as pd
import decimal

from stocks.models import stockABS, Listing, convertToDate
from stocks.models import Stocktradedate

__author__ = 'pchaos'


class RPSBase(stockABS):
    code = models.ForeignKey(Listing, verbose_name='代码', on_delete=models.PROTECT)
    rps120 = models.DecimalField(verbose_name='RPS120', max_digits=7, decimal_places=3, null=True)
    rps250 = models.DecimalField(verbose_name='RPS250', max_digits=7, decimal_places=3, null=True)
    tradedate = models.DateField(verbose_name='交易日期', db_index=True)

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

    @classmethod
    def updateSaved(cls, qssaved):
        with transaction.atomic():
            for val in qssaved:
                # 更新日期在原来保存区间的数据,需要单个更新
                val.index = pd.RangeIndex(len(val.index))
                for ind in val.index:
                    v = val.iloc[ind]
                    rps = cls.objects.get(tradedate=val['tradedate'][0], code_id=v['code_id'])
                    rps.rps120 = v['rps120']
                    rps.rps250 = v['rps250']
                    rps.save()

    class Meta:
        abstract = True


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
            # dfd.index = pd.RangeIndex(len(dfd.index))
            rpsname = 'rps{}'.format(str(n))
            rpsn = dfd[[rpsname, 'code_id']]
            rpsn = rpsn[rpsn[rpsname].apply(lambda x: float(x) > -99)]  # 处理Nan数据
            rpsn = rpsn.sort_values(by=[rpsname])
            # rpsn.reset_index(inplace=True)
            rpsn.index = pd.RangeIndex(len(rpsn.index))
            rpsn['a'] = np.round(100 * (rpsn.index - rpsn.index.min()) / (rpsn.index.max() - rpsn.index.min()), 2)
            rpsn.set_index('code_id', inplace=True)
            dfd.set_index('code_id', inplace=True)
            if (rpsname not in list(dfd.columns)):
                # 结果集中没有rpsname列名，则增加空列
                dfd[rpsname] = pd.np.nan
            dfd.loc[:, (rpsname)] = rpsn['a']
        # NaN 设置成 -1
        dfd['rps250'] = dfd['rps250'].apply(lambda x: x if (float(x) > -99) else -1)
        dfd.reset_index(inplace=True)
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
            for v in Stocktradedate.get_real_datelisting(start, end).values('tradedate'):
                print(v)
                # 获取 v['tradedate']对应的指数列表
                qsday = qs.filter(tradedate=v['tradedate'])
                df = pd.DataFrame(list(qsday.values()))
                data = RPS.caculateRPS(df)
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
        except Exception as e:
            print(e.args)
        return cls.getlist('index')

    @classmethod
    def importStockListing(cls, start=None, end=None, ignoreSaved=True):
        """ 插入所有股票RPS

        :param start: 计算的开始日期
        :param end:
        :param ignoreSaved: Boolean 是否重新计算已保存的RPS
        :return:
        """
        """ 

        :return:
        """
        stocktype = 'stock'
        if start is None:
            # 数据库中最大的已计算日期
            latest = cls.getlist('stock').aggregate(Max('tradedate'))['tradedate__max']
            if latest:
                start = cls.getNearestTradedate(latest, -5)
            else:
                start = '2014-1-1'
        if end is None:
            #  获取当天
            end = datetime.datetime.now().date()
        qs = RPSprepare.getlist(stocktype)
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = []  # quantaxis中无数据时，保存到delisted
            qssaved = []
            for v in Stocktradedate.get_real_datelisting(start, end).values('tradedate'):
                print('dealing ... {}'.format(v['tradedate']))
                # 获取 v['tradedate']对应的股票RPS预计算列表
                qsday = qs.filter(tradedate=v['tradedate'])
                if ignoreSaved:
                    if qsday.count() == cls.getlist(stocktype).filter(tradedate=v['tradedate']).count():
                        # RPS预计算数量和已保存的RPS数量相同，则跳过
                        # print('pass')
                        continue
                df = pd.DataFrame(list(qsday.values()))
                data = RPS.caculateRPS(df)
                del data['id']
                # code = Listing.objects.get(code=v.code.code, category=11)
                if len(data) > 0:
                    df, dfsaved = cls.dfNotInModel(data, v['tradedate'])
                    if len(df) == 0 and len(dfsaved) > 0:
                        # 当天所有数据都要更新
                        cls.getlist(stocktype).filter(tradedate=v['tradedate']).delete()
                        cls.savedf(data, isBuckCreate=True)
                        continue
                    if len(df) > 0:
                        cls.savedf(df, isBuckCreate=True)
                        print('saved:{}'.format(len(df)))
                    if len(dfsaved) > 0:
                        # 日期在原来保存区间的数据
                        qssaved.append(dfsaved)
                        print('append to later save:{}'.format(len(dfsaved)))
                else:
                    # quantaxis中无数据
                    delisted.append(v['tradedate'])
            print('delisted count {} :\n {}'.format(len(delisted), delisted))
            cls.updateSaved(qssaved)
            print('保存过的数据更新数量 {} :\n {}'.format(len(qssaved), qssaved))
        except Exception as e:
            print(e.args)
        return cls.getlist(stocktype)

    @classmethod
    def dfNotInModel(cls, df, tradedate):
        """ 查询df不在数据库时间大于等于tradedate中的数据

        :param df:
        :param code_id:  股票代码id
        :param start: 起始日期
        :return: df不在数据库时间大于等于tradedate中的dataframe， df在数据库时间大于等于tradedate中的需要单独更新的数据dataframe
        """
        if len(df) == 0:
            return pd.DataFrame(), pd.DataFrame()

        # 保存过的不再保存
        qs = cls.getlist('stock').filter(tradedate=tradedate)
        if qs.count() > 0:
            q = qs.values('tradedate', 'rps120', 'rps250', 'code_id')
            df2 = pd.DataFrame.from_records(q)
            df2['rps120'] = df2['rps120'].apply(lambda x: float(x)).astype(float)
            df2['rps250'] = df2['rps250'].apply(lambda x: float(x)).astype(float)
            df = cls.dfNotInAnotherdf(df, df2)
            # print(df)

            return df[~(df['tradedate'] <= df2['tradedate'].max()) & (df['tradedate'] >= df2['tradedate'].min())], \
                   df[(df['tradedate'] <= df2['tradedate'].max()) & (df['tradedate'] >= df2['tradedate'].min())]
        return df, pd.DataFrame()

    @classmethod
    def RPSIntensity(cls, intensity=90, start=None, end=None, period=250, stocktype='stock'):
        """ 查询起止时间介于（satrt，end）之间，RPS强度大于intensity的股票

        :param intensity: RPS强度
        :param start: 开始日期
        :param end:  结束日期
        :param period: 查询RPS周期 目前股票支持120日、250日
        :param stocktype: 股票：'stock'， 指数： 'index'
        :return:
        """
        start = cls.getNearestTradedate(start)
        end = cls.getNearestTradedate(end)
        if period == 250:
            return cls.RPS250Intensity(intensity, start, end, stocktype)
        else:
            return cls.RPS120Intensity(intensity, start, end, stocktype)

    @classmethod
    def RPS250Intensity(cls, intensity=90, start=None, end=None, stocktype='stock'):
        """ 查询周期为250日起止时间介于（satrt，end）之间，RPS强度大于intensity

        :param intensity: RPS强度
        :param start: 开始日期
        :param end:  结束日期
        :param stocktype: 股票：'stock'， 指数： 'index'
        :return:
        """
        if start == end:
            # 查询某一天的RPS
            return cls.getlist(stocktype).filter(tradedate=start, rps250__gte=intensity).exclude(
                rps250=decimal.Decimal('NaN'))
        else:
            qs = cls.getlist(stocktype).filter(tradedate__range=(start, end), rps250__gte=intensity).exclude(
                rps250=decimal.Decimal('NaN')).values('code').distinct()
            return cls.getlist(stocktype).filter(tradedate__range=(start, end), code__in=qs.values('code')).exclude(
                rps250=decimal.Decimal('NaN'))

    @classmethod
    def RPS120Intensity(cls, intensity=90, start=None, end=None, stocktype='stock'):
        if start == end:
            # 查询某一天的RPS
            return cls.getlist(stocktype).filter(tradedate=start, rps120__gte=intensity).exclude(
                rps120=decimal.Decimal('NaN'))
        else:
            qs = cls.getlist(stocktype).filter(tradedate__range=(start, end), rps120__gte=intensity).exclude(
                rps120=decimal.Decimal('NaN')).values('code').distinct()
            return cls.getlist(stocktype).filter(tradedate__range=(start, end), code__in=qs.values('code')).exclude(
                rps120=decimal.Decimal('NaN'))

    class Meta:
        # app_label ='rps计算'
        verbose_name = '欧奈尔PRS'
        unique_together = (('code', 'tradedate'))


class RPSprepare(RPSBase):
    """欧奈尔PRS预计算

    """

    class Meta:
        # app_label ='rps计算中间量'
        verbose_name = 'RPS基础'
        unique_together = (('code', 'tradedate'))

    @classmethod
    def importIndexListing(cls, start='2014-1-1'):
        """ 插入所有股票指数
            qa.QA_fetch_index_day_adv(v['code'], '1990-01-01', datetime.datetime.now().strftime("%Y-%m-%d"))

    已知重复的指数代码：
    000300 399300
    000901 399901
    000903 399903
    000922 399922
    000925 399925
    000928 399928
    000931 399931
    000934 399934
    000935 399935
    000939 399939
    000944 399944
    000950 399950
    000951 399951
    000957 399957
    000958 399958
    000961 399961
    000963 399963
    000969 399969
    000977 399977
    000979 399979

        :return:
        """
        codelist = Listing.getlist('index')
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = []  # quantaxis中无数据list
            with transaction.atomic():
                for v in codelist.values():
                    print('dealing: {}'.format(v))
                    # get stockcode
                    code = Listing.objects.get(code=v['code'], category=11)
                    # 本地获取指数日线数据
                    data = qa.QA_fetch_index_day_adv(v['code'], '1990-01-01',
                                                     datetime.datetime.now().strftime("%Y-%m-%d"))
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

    @classmethod
    def importStockListing(cls, start=None):
        """ 插入所有股票RPS预备数据

        :return:
        """
        if start is None:
            # 数据库中最大的已计算日期
            latest = cls.getlist('stock').aggregate(Max('tradedate'))['tradedate__max']
            if latest:
                start = cls.getNearestTradedate(latest, -5)
            else:
                start = '2014-1-1'
        codelist = Listing.getlist('stock')
        # todo 如果已经插入，则判断是否有更新
        try:
            # 批量创建对象，减少SQL查询次数
            querysetlist = []
            delisted = []  # quantaxis中无数据list
            qssaved = []
            tdate = cls.getNearestTradedate()
            realStart120 = cls.getNearestTradedate(start, -120)
            realStart = cls.getNearestTradedate(start, -250)
            # with transaction.atomic():
            # for v in codelist.values()[11:100]:
            for v in codelist.values():
                print('Dealing {} {} {}'.format(format(v['id'], '05d'), v['code'], v['name']))
                try:
                    # get stockcode
                    code = Listing.objects.get(code=v['code'], category=10)
                    # 本地获取指数日线数据
                    data = qa.QA_fetch_stock_day_adv(v['code'], realStart,
                                                     datetime.datetime.now().strftime("%Y-%m-%d")).to_qfq()
                    if len(data) > 120:
                        df = pd.DataFrame(data.close)
                        df['rps120'] = round(df.close / df.close.shift(120), 3)
                        df['rps250'] = round(df.close / df.close.shift(250), 3)
                        del df['close']
                        if code.timeToMarket > realStart120:
                            # 上市日期较早
                            cutDay = 120
                        else:
                            cutDay = 250
                        df = df[cutDay:]
                        df.reset_index(inplace=True)
                        df.columns = ['tradedate', 'code', 'rps120', 'rps250']
                        del df['code']
                        df['tradedate'] = df['tradedate'].apply(lambda x: convertToDate(str(x)[:10])).astype(
                            datetime.date)
                        df['code_id'] = code.id
                        df, dfsaved = cls.dfNotInModel(df, code.id, df['tradedate'].min())
                        if len(df) > 0:
                            # print(df)
                            cls.savedf(df)
                        if len(dfsaved) > 0:
                            # 日期在原来保存区间的数据
                            qssaved.append(dfsaved)

                except Exception as e:
                    delisted.append(v['code'])
                    print(len(delisted), e.args)
                    # print(df)

            cls.updateSaved(qssaved)

            print('保存过的数据更新数量 {} \n {}'.format(len(qssaved), qssaved))
            print('delisted count {} :\n {}'.format(len(delisted), delisted))
            # RPSprepare.objects.bulk_create(querysetlist)
        except Exception as e:
            print(e.args)
        return cls.getlist('stock')

    @classmethod
    def dfNotInModel(cls, df, code_id, start):
        """ 查询df不再数据库中的数据

        :param df:
        :param code_id:  股票代码id
        :param start: 起始日期
        :return: dataframe
        """
        # 保存过的不再保存
        if len(df) == 0:
            return pd.DataFrame(), pd.DataFrame()

        qs = cls.getlist('stock').filter(tradedate__gte=start, code_id=code_id)
        if qs.count() > 0:
            q = qs.values('tradedate', 'rps120', 'rps250', 'code_id')
            df2 = pd.DataFrame.from_records(q)
            df2['rps120'] = df2['rps120'].apply(lambda x: float(x)).astype(float)
            df2['rps250'] = df2['rps250'].apply(lambda x: float(x)).astype(float)
            df = cls.dfNotInAnotherdf(df, df2)
            # print(df)

            return df[~(df['tradedate'] <= df2['tradedate'].max()) & (df['tradedate'] >= df2['tradedate'].min())], \
                   df[(df['tradedate'] <= df2['tradedate'].max()) & (df['tradedate'] >= df2['tradedate'].min())]
        return df, pd.DataFrame()
