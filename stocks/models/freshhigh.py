# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : freshhigh.py

Description :

@Author :       pchaos

date：          18-7-9
-------------------------------------------------
Change Activity:
               18-7-9:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.db import models
from django.db.models import Q, Max
from django.db import transaction
import datetime
import pandas as pd

from stocks.models import StockBase
from stocks.models import Listing, RPS
import QUANTAXIS as qa


class FreshHigh(StockBase):
    """ 创新高后，最低点和最高价记录

    """
    code = models.ForeignKey(Listing, verbose_name='代码', max_length=10, on_delete=models.PROTECT, db_index=True,
                             null=True)
    high = models.DecimalField(verbose_name='最高价', max_digits=9, decimal_places=3, null=True)
    low = models.DecimalField(verbose_name='最低价', max_digits=9, decimal_places=3, null=True)
    htradedate = models.DateField(verbose_name='最高点日期', null=True, db_index=True)
    ltradedate = models.DateField(verbose_name='最低点日期', null=True, db_index=True)

    @classmethod
    def importList(cls, start=None, end=datetime.datetime.now().date(), n=120, m=250):
        """ 创一年新高后，最低点和最高价记录

        :param start:
        :param end:
        :param n:
        :param m:
        :return:
        """

        def firstHigh(code, start=None, end=datetime.datetime.now().date(), n=120, m=250):
            """ 返回第一次新高

            :param code:
            :param start:
            :param end:
            :param n:
            :param m:
            :return:
            """
            def cmpfuncPeriod(df, days):
                # 标记创半年新高
                return pd.DataFrame(df.high == df.high.rolling(days).max())

            # 半年新高
            tdate = Listing.getNearestTradedate(days=-(n + m))

            data = qa.QA_fetch_stock_day_adv(code, start=tdate, end=end).to_qfq()
            ind = data.add_func(lambda x: cmpfuncPeriod(x, m))
            results = ind[ind['high']]
            df = data[ind.high].data.high.reset_index()
            # gg = df.groupby('code').date.first() # 更快速？
            usedcode = []
            fh = []
            for v in [df.iloc[a] for a in df.index]:
                if not (v.code in usedcode):
                    # 创新高的股票代码
                    usedcode.append(v.code)
                    fh.append([v.date, v.code])
            return pd.DataFrame(fh, columns=['date', 'code'])

        if not start:
            # 默认根据n，m周期计算获取数据开始日期
            start = cls.getNearestTradedate(days=-(n))

        # 查找大于start日期的RPS强度
        code = pd.DataFrame(list(RPS.getlist().filter(tradedate__gte=start, tradedate__lte=end).filter(
            (Q(rps120__gte=90) & Q(rps250__gte=80)) | (Q(rps120__gte=80) & Q(rps250__gte=90))). \
                                 values('code__code').distinct()))['code__code'].values.tolist()
        df = firstHigh(code, start, end, n, m)
        for v in [df.iloc[a] for a in df.index]:
            print(v.code, v.date)
            try:
                day_data = qa.QA_fetch_stock_day_adv(v.code, v.date, end).to_qfq()
                ddf = day_data.data[['high', 'close', 'low']].reset_index()
                ddf['high'] = ddf['high'].apply(lambda x: round(x, 3))
                ddf['close'] = ddf['close'].apply(lambda x: round(x, 3))
                ddf['low'] = ddf['low'].apply(lambda x: round(x, 3))
                ddf['date'] = ddf['date'].apply(lambda x: x.date())
                c = Listing.getlist('stock').get(code=v['code'])
                qs = cls.objects.all().filter(code=c).aggregate(Max("ltradedate"))
                if qs['ltradedate__max']:
                    ddf = ddf[ddf['date'].apply(lambda x: x >= qs['ltradedate__max'])]
                entries = ddf.to_dict('records')
                cls.updateHigh(c, entries)

            except Exception as e:
                print(e.args)

    @classmethod
    def updateHigh(cls, code, entries):
        h = l = 0
        for v in entries:
            if h == 0:
                # 第一条记录，查询时候有历史数据
                ld = cls.objects.all().filter(code=code).aggregate(Max("ltradedate"))['ltradedate__max']
                qs = cls.objects.all().filter(code=code, ltradedate=ld)
                if qs.count() > 0:
                    # 有历史数据
                    val = qs.values().first()
                    l = val['low']
                    h = val['high']
                    hd = val['htradedate']
                    # cls.update(code, val['high'], val['htradedate'],l, v['date'])

            if h < v['high']:
                if h > 0 and l > v['low']:
                    # 不是第一次保存，并且最低价不是最后的最低价 （可能会出现新高以后再出现最低价，这个情况暂不考虑）
                    cls.update(code, h, hd, l, v['date'])
                h = v['high']
                l = v['close']
                hd = v['date']
                _, created = cls.objects.get_or_create(code=code, high=h, low=l, htradedate=v['date'],
                                                       ltradedate=v['date'])
            else:
                if l > v['low']:
                    l = v['low']
                    cls.update(code, h, hd, l, v['date'])

    @classmethod
    def update(cls, code, high, htradedate, low, ltradedate):
        try:
            freshhigh = cls.objects.get(code=code, htradedate=htradedate)
            freshhigh.low = low
            freshhigh.ltradedate = ltradedate
            freshhigh.save()
        except Exception as e:
            raise Exception(e)

    def __str__(self):
        return '{} {} {} {} {} '.format(self.code, self.high, self.htradedate, self.low, self.ltradedate)

    class Meta:
        verbose_name = '创一年新高'
        unique_together = (('code', 'htradedate'))
