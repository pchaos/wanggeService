# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_quantaxis.py

Description :

@Author :       pchaos

tradedate：          2018-5-6
-------------------------------------------------
Change Activity:
               2018-5-6:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.test import TestCase
import datetime
import QUANTAXIS as qa
from QUANTAXIS.QAFetch import QATdx as tdx
from QUANTAXIS.QAFetch.QATdx import ping
import numpy as np
import pandas as pd
from stocks.models import Listing, STOCK_CATEGORY

"""
QA.QA_util_log_info('日线数据')
QA.QA_util_log_info('不复权')  
data=QA.QAFetch.QATdx.QA_fetch_get_stock_day('00001','2017-01-01','2017-01-31')

QA.QA_util_log_info('前复权')
data=QA.QAFetch.QATdx.QA_fetch_get_stock_day('00001','2017-01-01','2017-01-31','01')

QA.QA_util_log_info('后复权')
data=QA.QAFetch.QATdx.QA_fetch_get_stock_day('00001','2017-01-01','2017-01-31','02')

QA.QA_util_log_info('定点前复权')
data=QA.QAFetch.QATdx.QA_fetch_get_stock_day('00001','2017-01-01','2017-01-31','03')


QA.QA_util_log_info('定点后复权')
data=QA.QAFetch.QATdx.QA_fetch_get_stock_day('00001','2017-01-01','2017-01-31','04')
"""


class testQuantaxis(TestCase):
    """ 测试quantaxis
        qa.QA_fetch_stock_day_adv
        qa.QAFetch.QATdx.QA_fetch_get_stock_list('stock')
        qa.QAFetch.QATdx.QA_fetch_get_index_day(code, '2017-01-01', '2017-09-01')
        qa.QAFetch.QATdx.QA_fetch_get_stock_list('index')
        qa.QA_fetch_index_day_adv(a.code, '1990-01-01', str(datetime.date.today()))

    """

    def setUp(self):
        self.code = '000001'

    def testQA_fetch_stock_day_adv(self):
        qa.logo = ''
        code = '600066'
        data = qa.QA_fetch_stock_day_adv(code, '2013-12-01', '2017-10-01')  # [可选to_qfq(),to_hfq()]
        s = qa.QAAnalysis_stock(data)
        # s 的属性是( < QAAnalysis_Stock > )
        '''
        s.open  # 开盘价序列
        s.close  # 收盘价序列
        s.high  # 最高价序列
        s.low  # 最低价序列
        s.vol  # 量
        s.volume  # 同vol
        s.tradedate  # 日期
        s.datetime
        s.index  # 索引
        s.price  # 平均价(O+H+L+C)/4
        s.mean  # price的平均数
        s.max  # price的最大值s
        s.min  # price的最小值
        s.mad  # price的平均绝对偏差
        s.mode  # price的众数(没啥用)
        s.price_diff  # price的一阶差分
        s.variance  # price的方差
        s.pvariance  # price的样本方差
        s.stdev  # price的标准差
        s.pstdev  # price的样本标准差
        s.mean_harmonic  # price的调和平均数
        s.amplitude  # price的振幅[极差]
        s.skewnewss  # price的峰度 (4阶中心距)
        s.kurtosis  # price的偏度 (3阶中心距)
        s.pct_change  # price的百分比变化序列
    
        s.add_func(QA.QA_indicator_CCI)  # 指标计算, 和DataStruct用法一致
        '''
        print(data)
        print(type(data))
        # print(s.close)
        # print(s.pct_change)

        # todo 测试前复权跨越分红周期后是否不同

    def test_codelist(self):
        codelist = qa.QA_fetch_stock_list_adv().code.tolist()
        self.assertTrue(len(codelist) > 3000, '股票数量应该大于3000只，实际{}只。'.format(len(codelist)))

    def test_loop_QA_fetch_stock_day_adv(self):
        # 导入股票列表
        # from .test_listing import TestListing
        # tsc = TestListing()
        Listing.importStockListing()
        listings = Listing.objects.all()
        df = pd.DataFrame()
        # codelist = []
        # for a in listings[:100]:
        #     codelist.append(a.code)

        for a in listings[:100]:
            code = a.code
            try:
                data = qa.QA_fetch_stock_day_adv(code, '2015-12-01', '2017-10-01').to_qfq()  # [可选to_qfq(),to_hfq()]
                print(data.code)
                dftmp = pd.DataFrame()
                # 120日rps
                # b = pd.DataFrame(data.data.close / data.data.close.shift(120))
                dftmp['rps120'] = pd.DataFrame(data.data.close / data.data.close.shift(120)).close
                # 250日rps
                b = pd.DataFrame(data.data.close / data.data.close.shift(250))
                dftmp['rps250'] = b.close
                df = df.append(dftmp.reset_index())
            except Exception as e:
                # print(e.args)
                qa.QA_util_log_info('{} {}'.format(code, e.args))
        df.set_index('date', inplace=True)
        day = '2017-9-29'
        # dfd = caculateRPS(df, day, [121, 251])
        dfd = self.caculateRPS(df, day, [120, 250])
        self.assertTrue(dfd[dfd['code'] == '000001'] is not None, 'result must not None!')
        # dfd = self.caculateRPS(df, day, [121, 250]) # 会报错

        # self.assertTrue(dfd.sort_values(by=['rps120'])['rps120'].equals(rps120.a), '按照code排序以后应该相同，{} != {}'.format(dfd['rps120'], rps120['a']))

    def caculateRPS(self, df, dateStr, nlist=[120, 250]):
        """
        计算n日rps
        :param df: dataframe
        :param dateStr: 计算rps的日期
        :param nlist: n日list
        :return:
        """
        dfd = df[df.index == dateStr]
        dfd.reset_index(inplace=True)
        # del dfd['tradedate']
        for n in nlist:
            dfd.reset_index(inplace=True)
            rpsname = 'rps{}'.format(str(n))
            rpsn = dfd[[rpsname, 'code']].sort_values(by=[rpsname])
            rpsn.reset_index(inplace=True)
            # del rpsn['index']
            rpsn['a'] = np.round(100 * (rpsn.index) / (rpsn.index.max() - rpsn.index.min()), 2)
            rpsn.set_index('code', inplace=True)
            dfd.set_index('code', inplace=True)
            if (rpsname not in list(dfd.columns)):
                # 结果集中没有rpsname列名，则增加空列
                dfd[rpsname] = pd.np.nan
            dfd.loc[:, (rpsname)] = rpsn['a']
        dfd.reset_index(inplace=True)
        dfd.set_index('date', inplace=True)
        return dfd[['code', 'rps120', 'rps250']]

    def test_QA_indicator_ma(self):
        """
        测试QA指标
        QUANTAXIS的指标系统
        QUANTAXIS的核心数据结构有一个方法叫add_func(func,*args,**kwargs),作为一个指标入口,会返回一个和DataStruct中股票数量一致长度的list

        QUANTAXIS有两种类型的指标:

        基础指标(输入为Series的指标)
        应用级指标(可应用于DataStruct的指标)
        其中,基础指标是为了应用级指标做准备的,及对应于Series的分析和dataframe的分析的关系

        基础类指标 [基本和同花顺/通达信一致]

        import QUANTAXIS as QA
        QA.MA(Series, N)
        QA.EMA(Series, N)
        QA.SMA(Series, N, M=1)
        QA.DIFF(Series, N=1)
        QA.HHV(Series, N)
        QA.LLV(Series, N)
        QA.SUM(Series, N)
        QA.ABS(Series)
        QA.MAX(A, B)
        QA.MIN(A, B)
        QA.CROSS(A, B)
        QA.COUNT(COND, N)
        QA.IF(COND, V1, V2)
        QA.REF(Series, N)
        QA.STD(Series, N)
        QA.AVEDEV(Series, N)
        QA.BBIBOLL(Series, N1, N2, N3, N4, N, M)
        应用级指标 add_func(func)

        import QUANTAXIS as QA
        QA.QA_indicator_OSC(DataFrame, N, M)
        QA.QA_indicator_BBI(DataFrame, N1, N2, N3, N4)
        QA.QA_indicator_PBX(DataFrame, N1, N2, N3, N4, N5, N6)
        QA.QA_indicator_BOLL(DataFrame, N)
        QA.QA_indicator_ROC(DataFrame, N, M)
        QA.QA_indicator_MTM(DataFrame, N, M)
        QA.QA_indicator_KDJ(DataFrame, N=9, M1=3, M2=3)
        QA.QA_indicator_MFI(DataFrame, N)
        QA.QA_indicator_ATR(DataFrame, N)
        QA.QA_indicator_SKDJ(DataFrame, N, M)
        QA.QA_indicator_WR(DataFrame, N, N1)
        QA.QA_indicator_BIAS(DataFrame, N1, N2, N3)
        QA.QA_indicator_RSI(DataFrame, N1, N2, N3)
        QA.QA_indicator_ADTM(DataFrame, N, M)
        QA.QA_indicator_DDI(DataFrame, N, N1, M, M1)
        QA.QA_indicator_CCI(DataFrame, N=14)
        自己写一个指标:

        比如 绝路航标

        import QUANTAXIS as QA
        def JLHB(data, m=7, n=5):

        通达信定义
        VAR1:=(CLOSE-LLV(LOW,60))/(HHV(HIGH,60)-LLV(LOW,60))*80;
        B:SMA(VAR1,N,1);
        VAR2:SMA(B,M,1);
        绝路航标:IF(CROSS(B,VAR2) AND B<40,50,0);

        var1 = (data['close'] - QA.LLV(data['low'], 60)) / \
            (QA.HHV(data['high'], 60) - QA.LLV(data['low'], 60)) * 80
        B = QA.SMA(var1, m)
        var2 = QA.SMA(B, n)
        if QA.CROSS(B,var2) and B[-1]<40:
            return 1
        else:
            return 0

        # 得到指标
        QA.QA_fetch_stock_day_adv('000001','2017-01-01','2017-05-31').to_qfq().add_func(JLHB)
            :return:
        """
        code = '603889'
        data = qa.QA_fetch_stock_day_adv(code, '2013-12-01', '2017-10-01')  # [可选to_qfq(),to_hfq()]
        s = qa.QAAnalysis_stock(data)
        n = 20
        values = qa.MA(data.CLOSE, n)
        print(values[:30])
        # print(QA.DIFF(data.CLOSE), 250)

        data = pd.Series(np.arange(100))
        values = qa.MA(data, n)
        data1 = pd.Series(np.arange(n - 1))
        data1 = data1.apply(lambda x: pd.np.nan)
        print(values[:n - 1], data1)
        self.assertTrue(values[:n - 1].equals(data1),
                        'Ma计算值前{}个应为NaN。长度：{} ： {}'.format(n, len(values[:n - 1]), len(data1)))
        self.assertTrue(values[n] > 0, 'Ma计算值前{}个应为大于零。'.format(n + 1))

    def test_QA_indicator_diff(self):
        """
         QA.DIFF 计算欧奈尔rps时，需要用到
        :return:
        """
        n = 1
        count = 100
        data = pd.Series(np.arange(count))
        values = qa.DIFF(data, n)
        data1 = pd.Series(np.arange(n))
        data1 = data1.apply(lambda x: pd.np.nan)
        print('{}\n{}'.format(values[:n], data1))
        self.assertTrue(values[:n].equals(data1),
                        'Ma计算值前{}个应为NaN。长度：{} ： {}'.format(n, len(values[:n - 1]), len(data1)))

        n = 10
        data = pd.Series(np.arange(count))
        values = qa.DIFF(data, n)
        data1 = pd.Series(np.arange(n))
        data1 = data1.apply(lambda x: pd.np.nan)
        self.assertTrue(values[:n].equals(data1),
                        'Ma计算值前{}个应为NaN。长度：{} ： {}'.format(n, len(values[:n - 1]), len(data1)))
        data1 = pd.Series(np.arange(count))
        data1 = data1.apply(lambda x: n)
        self.assertTrue(values[n] == (data1[n]),
                        'Ma计算值前{}个应为NaN。\n{}\n{}\n长度：{} ： {}'.format(n, values[n:], data1[n:], len(values[n:]),
                                                                     len(data1[n:])))

    def test_QA_indicator_atr(self):
        n = 14
        code = '000001'
        data = qa.QA_fetch_stock_day_adv(code, '2016-12-01', '2017-02-01')  # [可选to_qfq(),to_hfq()]
        s = qa.QAAnalysis_stock(data)
        # 传入为pd dataframe
        qaatr = qa.QA_indicator_ATR(s.data, n)
        qr = qaatr > 0
        self.assertTrue(not qr.iloc[0].ATR, '第一个ATR应该为空：{}'.format(qr.iloc[0].ATR))
        self.assertTrue(qr.iloc[n].ATR, '第{}个ATR不应该为空：{}'.format(n, qr.iloc[n].ATR))
        '''
        获取周线数据
        from QUANTAXIS.QAUtil.QAParameter import FREQUENCE
        (QA_quotation('000001', '2017-01-01', '2017-01-31', frequence=FREQUENCE.DAY,
                      market=MARKET_TYPE.STOCK_CN, source=DATASOURCE.TDX, output=OUTPUT_FORMAT.DATAFRAME))

        '''

    def test_QA_indicator_stocklist(self):
        # 获取股票代码列表
        qa.QA_util_log_info('stock列表')
        data = qa.QAFetch.QATdx.QA_fetch_get_stock_list('stock')
        print(data.loc['000001'])
        self.assertTrue(data.loc['000001'].volunit is not None, '未获取股票代码列表:{}'.format(data))

    def test_QA_fetch_indexList(self):
        qa.QA_util_log_info('指数列表')
        data = qa.QAFetch.QATdx.QA_fetch_get_stock_list('index')
        # data['name']包含字符 '399'
        a = data.code.str.find('399') != -1
        # data.loc[a, 'code']
        self.assertTrue(data['code'].count() > 0, '未找到指数')
        self.assertTrue(data.loc[a, 'code'].count() > 0, '未找到指数')
        self.assertTrue(data['code'].count() > data.loc[a, 'code'].count(), '指数全局比局部小？')

    def test_QA_fetch_ETFList(self):
        qa.QA_util_log_info('ETF列表')
        data = qa.QAFetch.QATdx.QA_fetch_get_stock_list('etf')
        # data['name']包含字符 '150'
        a = data.code.str.find('150') != -1
        # data.loc[a, 'code']
        self.assertTrue(data['code'].count() > 0, '未找到分级基金')
        self.assertTrue(data.loc[a, 'code'].count() > 0, '未找到分级基金')

    def test_QA_indicator_tradedate(self):
        """测试易日期

        :return:
        """
        data = qa.QA_fetch_trade_date()
        for a in data:
            print(a)
        self.assertTrue(len(data) > 250 * 20, '2018年,总交易日期数大于20*250天：{}'.format(len(data)))

    def test_QA_fetch_index(self):
        # 从网上获取指数/基金日线
        qa.QA_util_log_info('从网上获取指数/基金日线')
        code = '000001'
        data = qa.QAFetch.QATdx.QA_fetch_get_index_day(code, '2017-01-01', '2017-09-01')
        self.assertTrue(data['code'].count() > 0, '未找到指数{}'.format(code))
        self.assertTrue(data.close.count() > 0, '未找到指数{}'.format(code))
        code = '150153'
        data = qa.QAFetch.QATdx.QA_fetch_get_index_day(code, '2017-01-01', '2017-09-01')
        self.assertTrue(data['code'].count() > 0, '未找到指数{}'.format(code))
        # 从本地获取指数/基金日线
        qa.QA_util_log_info('从本地获取指数/基金日线')
        data = qa.QA_fetch_index_day_adv(code, '2017-01-01', '2017-09-01')
        qa.QA_util_log_info(data)
        self.assertTrue(data.close.count() > 0, '未找到指数{}'.format(code))
        # self.assertTrue(data['code'].count() > 0, '未找到指数{}'.format(code)) 这样写会报错,返回结果为：QA_DataStruct_Index_day

    def test_QA_fetch_indexlisting(self):
        # 从网上获取指数/基金日线
        qa.QA_util_log_info('从网上获取指数/基金日线')
        df = qa.QAFetch.QATdx.QA_fetch_get_stock_list('index')
        querysetlist = []
        for i in df.index[:10]:
            a = df.loc[i]
            # 本地获取指数日线数据
            data = qa.QA_fetch_index_day_adv(a.code, '1990-01-01', str(datetime.date.today()))
            """
            从本地数据库获取数据
            data = qa.QA_fetch_index_day_adv(a.code, '1990-01-01', datetime.now().strftime("%Y-%m-%d"))
            从网络获取数据
            data = qa.QAFetch.QATdx.QA_fetch_get_index_day(code, '2017-01-01', '2017-09-01')
            """
            d = data.data.date[0].strftime("%Y-%m-%d")
            if a.sse == 'sh':
                market = 1
            else:
                market = 0
            category = 11
            querysetlist.append(
                Listing(code=a.code, name=a['name'], timeToMarket=d, volunit=a.volunit, decimalpoint=a.decimal_point,
                        category=category, market=market))
        Listing.objects.bulk_create(querysetlist)
        self.assertTrue(Listing.getlist('index').count() > 0, '未插入成功:{}'.format(querysetlist))

    def test_block(self):
        data = qa.QAFetch.QATdx.QA_fetch_get_stock_block()
        btype = set(data.type)
        self.assertTrue(len(btype) < 10, '版块类型不超过10，实际类型数：{}'.format(len(btype)))
        gtype = data[data.type == 'gn']
        self.assertTrue(len(gtype) > 100, '版块类型不少于100，实际类型数：{}'.format(len(gtype)))

        for i in set(data[data.type == 'gn'].blockname):
            # 版块名会重复
            if len(set(data[data.blockname == i].type)) > 1:
                print('** {} {}'.format(i, set(data[data.blockname == i].type)))

        """ set(data.source)
           {'tdx'}
        """
        self.assertTrue(set(data.source) == {'tdx'}, '版块来源数大于一个，为 {}'.format(set(data.source)))

    def test_useraddfunc(self):
        from django.db.models import Q
        from stocks.models import Listing, RPS

        def cmpfunc(df):
            # 标记创新高
            return pd.DataFrame(df.high == df.high.max())

        def cmpfunc120(df):
            # 标记创半年新高
            return pd.DataFrame(df.high == df.high.rolling(120).max())

        def cmpfuncPeriod(df, days):
            # 标记创半年新高
            return pd.DataFrame(df.high == df.high.rolling(days).max())

        def higher(df):

            return ind[ind['high']]

        # tdate = HSGTCGHold.getNearestTradedate(days=-120)
        tdate = '2018-1-2'
        end = datetime.datetime.now().date()
        code = qa.QA_fetch_stock_list_adv().code.tolist()
        data = qa.QA_fetch_stock_day_adv(code, start=tdate, end=end).to_qfq()
        ind = data.add_func(lambda x: x.tail(20).high.max() == x.high.max())
        code = list(ind[ind].reset_index().code)
        # 半年新高
        code = pd.DataFrame(list(RPS.getlist().filter(tradedate__gte='2018-1-1').filter(
            (Q(rps120__gte=90) & Q(rps250__gte=80)) | (Q(rps120__gte=80) & Q(rps250__gte=90))). \
                                 values('code__code').distinct()))['code__code'].values.tolist()
        n = 120
        m = 120  # 新高范围
        df = self.firstHigh(code, end, m, n)
        for v in [df.iloc[a] for a in df.index]:
            print(v.code, v.date)
            try:
                day_data = qa.QA_fetch_stock_day_adv(v.code, v.date, end).to_qfq()
                ddf = day_data.data[['high', 'close', 'low']].reset_index()
            except Exception as e:
                print(e.args)

        n = 120
        m = 250
        # tdate = Listing.getNearestTradedate(days=-(n * 2))
        tdate = Listing.getNearestTradedate(days=-(n + m + 2))
        data = qa.QA_fetch_stock_day_adv(code, start=tdate, end=end).to_qfq()
        ind = data.add_func(cmpfunc120)
        # ind1 = data.add_func(lambda x: cmpfuncPeriod(x, n))
        ind1 = data.add_func(lambda x: cmpfuncPeriod(x, m))
        results = ind[ind['high']]
        assert ind[ind['high']].equals(ind1[ind1['high']])

        df = data[ind.high].data.high.reset_index()
        usedcode = []
        for v in [df.iloc[a] for a in df.index]:
            if not (v.code in usedcode):
                # 创新高的股票代码
                usedcode.append([v.date, v.code, v.high])

        data = qa.QA_fetch_stock_day_adv(code, start=tdate, end=end).to_qfq()
        # 收盘在50日线之上
        ind = data.add_func(lambda x: float(qa.QA_indicator_MA(x.tail(50), 50)[-1:].MA) <= float(x.tail(1).close))
        code = list(ind[ind].reset_index().code)

        # 前100日内有连续两天wr==0
        day_data = qa.QA_fetch_stock_day_adv(code, '2018-01-03', '2018-07-04')
        ind = day_data.add_func(qa.QA_indicator_WR, 10, 6)
        res = ind.groupby(level=1, as_index=False, sort=False, group_keys=False).apply(
            lambda x: (x.tail(100))['WR1'].rolling(2).sum() == 0)
        print(res[res])

    def firstHigh(self, code, end, m, n):
        def cmpfuncPeriod(df, days):
            # 标记创半年新高
            return pd.DataFrame(df.high == df.high.rolling(days).max())

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

    def test_QATdx_QA_fetch_get_stock_day(self):
        code = '000002'
        data = qa.QAFetch.QATdx.QA_fetch_get_stock_day(code, '2017-01-01',
                                                       datetime.datetime.now().date().strftime("%Y-%m-%d"))
        data1 = qa.QAFetch.QATdx.QA_fetch_get_stock_day(code, '2017-01-01', '2018-7-10')
        self.assertTrue(not data.equals(data1), '结束时间不同，获得数据应该不相同：{} {}'.format(data, data1))

    def test_QATdx_QA_fetch_get_stock_day_resample(self):
        def resample(df, period='w'):
            # https://pandas-docs.github.io/pandas-docs-travis/timeseries.html#offset-aliases
            # 周 W、月 M、季度 Q、10天 10D、2周 2W
            df = df.reset_index().set_index('date', drop=False)
            weekly_df = df.resample(period).last()
            weekly_df['open'] = df['open'].resample(period).first()
            weekly_df['high'] = df['high'].resample(period).max()
            weekly_df['low'] = df['low'].resample(period).min()
            weekly_df['close'] = df['close'].resample(period).last()
            weekly_df['date'] = df['date'].resample(period).last()
            weekly_df['volume'] = df['volume'].resample(period).sum()
            weekly_df['amount'] = df['amount'].resample(period).sum()
            # 去除空的数据（没有交易的周）
            weekly_df = weekly_df[weekly_df.close.notnull()]
            weekly_df.reset_index(inplace=True, drop=True)
            return weekly_df.set_index('date')

        code = '000002'
        tdate = '2017-1-1'
        end = datetime.datetime.now().date() - datetime.timedelta(10)
        data = qa.QA_fetch_stock_day_adv(code, start=tdate, end=end)
        # data = qa.QA_fetch_stock_day_adv(code, start=tdate, end=end).to_qfq()
        df = data.add_func(lambda x: resample(x, 'w'))
        # df = data.add_func(lambda x: resample(x, 'm'))
        df = data.data.reset_index(drop=True)

        code = '000002'
        tdate = '2017-1-1'
        end = datetime.datetime.now().date() - datetime.timedelta(10)
        end = Listing.getNearestTradedate(end)
        data = qa.QA_fetch_stock_day_adv(code, start=tdate, end=end)
        data1 = qa.QAFetch.QATdx.QA_fetch_get_stock_day(code, '2017-01-01', end.strftime("%Y-%m-%d"), frequence='w')

        data2 = data.add_func(lambda x: qa.QA_data_day_resample(x))
        self.assertTrue(len(data1) == len(data2), '长度不匹配。data1 len:{}, data2 len:{}'.format(len(data1), len(data2)))
        self.assertTrue(
            data1[['close', 'open', 'high', 'vol', 'amount']].equals(data2[['close', 'open', 'high', 'vol', 'amount']]),
            'data1:{}, data2: {}'.format(data1[['close', 'open', 'high', 'vol', 'amount']],
                                         data2[['close', 'open', 'high', 'vol', 'amount']]))

    def test_QATdx_QA_fetch_get_stock_day_multithread(self):
        # 多线程获取日线数据
        # stock_ip 60.191.117.167 future_ip 106.14.95.149 119.147.164.60 119.147.171.206
        """
        BAD RESPONSE 115.238.56.198
BAD RESPONSE 115.238.90.165
BAD RESPONSE 117.184.140.156
BAD RESPONSE 119.147.164.60
BAD RESPONSE 119.147.171.206
BAD RESPONSE 119.29.51.30
BAD RESPONSE 121.14.104.70
BAD RESPONSE 121.14.104.72
BAD RESPONSE 121.14.110.194
BAD RESPONSE 121.14.2.7
BAD RESPONSE 123.125.108.23
BAD RESPONSE 123.125.108.24
BAD RESPONSE 124.160.88.183
BAD RESPONSE 180.153.18.17
BAD RESPONSE 180.153.18.170
BAD RESPONSE 180.153.18.171
BAD RESPONSE 180.153.39.51
BAD RESPONSE 218.108.47.69
BAD RESPONSE 218.108.50.178
BAD RESPONSE 218.108.98.244
BAD RESPONSE 218.75.126.9
BAD RESPONSE 218.9.148.108
BAD RESPONSE 221.194.181.176
BAD RESPONSE 59.173.18.69
BAD RESPONSE 60.12.136.250
BAD RESPONSE 60.191.117.167
BAD RESPONSE 60.28.29.69
BAD RESPONSE 61.135.142.73
BAD RESPONSE 61.135.142.88
BAD RESPONSE 61.152.107.168
BAD RESPONSE 61.152.249.56
BAD RESPONSE 61.153.144.179
BAD RESPONSE 61.153.209.138
BAD RESPONSE 61.153.209.139
BAD RESPONSE hq.cjis.cn
BAD RESPONSE hq1.daton.com.cn
BAD RESPONSE jstdx.gtjas.com
BAD RESPONSE shtdx.gtjas.com
        :return:
        """

        import time
        import multiprocessing
        # from multiprocessing.dummy import Pool
        from multiprocessing.dummy import Pool
        # Get all worker processes
        cores = multiprocessing.cpu_count()

        # Start all worker processes

        codelist = qa.QA_fetch_stock_list_adv().code.tolist()
        codeListCount = 300
        start = '2018-07-01'
        end = '2019-01-01'
        ips = getStockIPList(qa.QAUtil.stock_ip_list)
        param = genParam(codelist[:codeListCount], start, end, IPList=ips[:cores])
        # for x in param:
        #     get_stock_day_map(x)
        # data = map(get_stock_day, param)
        # data = map(get_stock_day_map, param)
        a = time.clock()
        with Pool(processes=cores) as pool:
            print("    | get_stock_day start.")
            # data = pool.starmap(get_stock_day, param)
            for i in range(cores):
                pLen = int(len(param) / cores) + 1
                data = pool.starmap_async(get_stock_day, param[int(i * pLen):int((i + 1) * pLen)])
            # print(data)
            pool.close()
            pool.join()
            print("    | get_stock_day done.")
        b = time.clock()
        t1 = b - a
        print('type of data :{}'.format(type(data)))
        data.get()
        # for v in data:
        #     print(v)
        # print('get results counts: {}'.format(len(data)))
        a = time.clock()
        print("    | get_stock_day start.")
        for code in codelist[:codeListCount]:
            get_stock_day(code, start, end, '00', 'day', ips[0]['ip'], ips[0]['port'])
        print("    | get_stock_day done.")
        b = time.clock()
        t2 = b - a
        print('最快的ip：{} {}'.format(ips[0]['ip'], ips[0]['port']))
        print('多线程时间：{}，单线程时间：{}'.format(t1, t2))

    def test_QATdx_QA_fetch_get_stock_day_multiProcess(self):
        import time
        import multiprocessing
        # Get all worker processes
        cores = multiprocessing.cpu_count()
        codelist = qa.QA_fetch_stock_list_adv().code.tolist()
        codeListCount = 300
        start = '2018-07-01'
        end = '2019-01-01'
        ips = getStockIPList(qa.QAUtil.stock_ip_list)
        param = genParam(codelist[:codeListCount], start, end, IPList=ips[:cores])
        a = time.clock()
        pl = ParallelSim()
        pl.add(get_stock_day, param)
        data = pl.get_results()
        b = time.clock()
        t1 = b - a
        # print('数量：{},多进程时间：{}'.format(len(param), t1))
        a = time.clock()
        print("    | get_stock_day start.")
        for code in codelist[:codeListCount]:
            get_stock_day(code, start, end, '00', 'day', ips[0]['ip'], ips[0]['port'])
        print("    | get_stock_day done.")
        b = time.clock()
        t2 = b - a
        print('最快的ip：{} {}'.format(ips[0]['ip'], ips[0]['port']))
        print('多线程时间：{}，单线程时间：{}'.format(t1, t2))

    def test_QAMA(self):
        # 计算MA
        # ind_list = qa.QAFetch.QATdx.QA_fetch_get_stock_list('index')
        code = ['000001', '399001', '399006']
        tdate = '2017-1-1'
        end = datetime.datetime.now().date() - datetime.timedelta(10)
        data = qa.QA_fetch_index_day_adv(code, start=tdate, end=end)
        self.assertTrue(len(data.index) > 100, '返回数据太少： {}'.format(len(data.index)))

    def test_QAMAS(self):
        # 计算MAS
        # ind_list = qa.QAFetch.QATdx.QA_fetch_get_stock_list('index')
        code = ['000001', '399001', '399006']
        tdate = '2017-1-1'
        # end = datetime.datetime.now().date() - datetime.timedelta(10)
        # data = qa.QA_fetch_index_day_adv(code, start=tdate, end=end)
        # self.assertTrue(len(data.index)> 100, '返回数据太少： {}'.format(len(data.index)))
        #
        # mas = mas_select(code)
        # self.assertTrue(len(mas.index) > 100, '返回数据太少： {}'.format(len(data.index)))
        # print(mas)
        # # 验证code为多个指数时，返回值是否和code为单个指数返回结果相同
        # for c in code:
        #     masc =mas_select(c)
        #     print('{}\n{}'.format(c, masc))
        #     # print(mas.loc[code[0]])
        #     # todo 绘制图片

        end = '2019-02-01'
        # data = qa.QA_fetch_index_day_adv(code, start=tdate, end=end)
        mas = mas_select(code, endDate=end)
        print(mas)
        # 验证code为多个指数时，返回值是否和code为单个指数返回结果相同
        for c in code:
            masc = mas_select(c, endDate=end)
            print('{}\n{}'.format(c, masc))
            # print(mas.loc[code[0]])
            # todo 绘制图片


# 定义均线强度，八条均线，
def mas_select(code, endDate=None, short=10, long=250):
    """
    :param code_list: 选股范围，默认全市场
    :param endDate: 选股日期，默认None为现在
    :param short: 短期均线
    :param long: 长期均线
    :return: 返回选后的股票列表
    """
    endDate = getOrCheckDate(endDate)
    data = qa_index_day(code, endDate, long)
    ind_data = data.add_func(QA_indicator_MAS)
    # # 选取最后两日的数据
    # lastDate, _ = ind_data.index[-1]
    # date = format(lastDate)
    # ind_1 = ind_data.xs(date, level=0)
    # ind_2 = ind_data.xs(qa.QA_util_get_last_day(date, 1), level=0)
    # # 最后两日都有数据的股票代码
    # code = list(set(ind_1.index) & set(ind_2.index))
    return ind_data


def qa_index_day(code_list, endDate=None, long=250):
    endDate = getOrCheckDate(endDate)
    long_days_ago = qa.QA_util_get_last_day(date=endDate, n=long)
    data = qa.QA_fetch_index_day_adv(code=code_list, start=long_days_ago, end=endDate)
    # data = data.to_qfq()  # 指数不需要复权
    return data


def getOrCheckDate(date=None):
    # 返回最后的交易日
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    if date is None:
        date = now
    date = qa.QA_util_get_real_date(date)
    if date == now and datetime.datetime.now().strftime('%H:%M') < '09:30':
        date = qa.QA_util_get_last_day(date, n=1)
    return date


def QA_indicator_MAS(DataFrame, *args, **kwargs):
    """ 计算均线、轮动

    Arguments:
        DataFrame {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    def MA(Series, N):
        return pd.Series.rolling(Series, N).mean()

    def MAS(Series, days):
        df = pd.DataFrame()
        # CLOSE = Series
        for N in days:
            df['MA{}'.format(N)] = MA(Series, N) <= Series
            df['MA{}'.format(N)] = df['MA{}'.format(N)].apply(lambda x: 1 if x else 0)
            print('ma{}'.format(N))
            print('Close')
            print(MA(Series, N)[-10:])
        print(Series[-10:])
        df['MAS'] = df.sum(axis=1)
        return df['MAS']

    days = [5, 13, 21, 34, 55, 89, 144, 233]
    CLOSE = DataFrame['close']
    MAS = MAS(CLOSE, days)
    return pd.DataFrame(MAS)


from multiprocessing import Pool, cpu_count


class ParallelSim(object):
    """ 多进程map类

    """

    def __init__(self, processes=cpu_count()):
        self.pool = Pool(processes=processes)
        self.total_processes = 0
        self.completed_processes = 0
        self.results = []
        self.data = None
        self.cores = processes  # cpu核心数量

    def add(self, func, iter):
        if isinstance(iter, list) and self.cores > 1:
            for i in range(self.cores):
                pLen = int(len(iter) / self.cores) + 1
                self.data = self.pool.starmap_async(func, iter[int(i * pLen):int((i + 1) * pLen)],
                                                    callback=self.complete)
                self.total_processes += 1
        else:
            self.data = self.pool.starmap_async(func=func, iterable=iter, callback=self.complete)
            self.total_processes += 1
        self.data.get()

    def complete(self, result):
        self.results.extend(result)
        self.completed_processes += 1
        print('Progress: {:.2f}%'.format((self.completed_processes / self.total_processes) * 100))

    def run(self):
        self.pool.close()
        self.pool.join()

    def get_results(self):
        return self.results


def get_stock_day(code, start_date, end_date, if_fq='00', frequence='day', ip=None, port=None):
    # print(code, ip, port)
    return tdx.QA_fetch_get_stock_day(code, start_date, end_date, if_fq, frequence, ip, port)


def get_stock_day_map(x):
    return tdx.QA_fetch_get_stock_day(x[0], x[1], x[2], x[3], x[4], x[5], x[6])


def getStockIPList(ip_list=[], n=0):
    ''' 根据ping排序返回可用的ip列表

    :param n: 最多返回的ip数量， 当可用ip数量小于n，返回所有可用的ip
    :return:
    '''
    import pickle
    import os
    filename = '/tmp/stockiplist.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as filehandle:
            # read the data as binary data stream
            results = pickle.load(filehandle)
            print('loading stock ip list.')
    else:
        data_stock = [(ping(x['ip'], x['port'], 'stock'), x) for x in ip_list]
        results = []
        for data, x in data_stock:
            # 删除ping不通的数据
            if data < datetime.timedelta(0, 9, 0):
                results.append((data, x))
        # 按照ping值从小大大排序
        results = [x[1] for x in sorted(results, key=lambda x: x[0])]
        with open(filename, 'wb') as filehandle:
            # store the data as binary data stream
            pickle.dump(results, filehandle)
            print('saving stock ip list.')
    if n == 0:
        return results
    else:
        return results[:n]


def genParam(codelist, start_date, end_date, if_fq='00', frequence='day', IPList=[]):
    count = len(IPList)
    my_iterator = iter(range(len(codelist)))
    return [(code, start_date, end_date, if_fq, frequence, IPList[i % count]['ip'], IPList[i % count]['port'])
            for code, i in [(code, next(my_iterator) % count) for code in codelist]]
