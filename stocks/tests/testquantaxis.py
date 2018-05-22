# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : testquantaxis.py

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
import numpy as np
import pandas as pd
from stocks.models import Listing, STOCK_CATEGORY


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
        s.max  # price的最大值
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


