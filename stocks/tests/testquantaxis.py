# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : testquantaxis.py

Description :

@Author :       pchaos

date：          2018-5-6
-------------------------------------------------
Change Activity:
               2018-5-6:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
__author__ = 'pchaos'

from django.test import TestCase
import QUANTAXIS as QA
import numpy as np
import pandas as pd


class testQuantaxis(TestCase):
    def testQA_fetch_stock_day_adv(self):
        QA.logo = ''
        code = '600066'
        data = QA.QA_fetch_stock_day_adv(code, '2013-12-01', '2017-10-01')  # [可选to_qfq(),to_hfq()]
        s = QA.QAAnalysis_stock(data)
        # s 的属性是( < QAAnalysis_Stock > )
        '''
        s.open  # 开盘价序列
        s.close  # 收盘价序列
        s.high  # 最高价序列
        s.low  # 最低价序列
        s.vol  # 量
        s.volume  # 同vol
        s.date  # 日期
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
        data = QA.QA_fetch_stock_day_adv(code, '2013-12-01', '2017-10-01')  # [可选to_qfq(),to_hfq()]
        s = QA.QAAnalysis_stock(data)
        n = 20
        values = QA.MA(data.CLOSE, n)
        print(values[:30])
        # print(QA.DIFF(data.CLOSE), 250)

        data = pd.Series(np.arange(100))
        values = QA.MA(data, n)
        data1 = pd.Series(np.arange(n - 1))
        data1 = data1.apply(lambda x: pd.np.nan)
        print(values[:n - 1], data1)
        self.assertTrue(values[:n - 1].equals(data1),
                        'Ma计算值前{}个应为NaN。长度：{} ： {}'.format(n, len(values[:n - 1]), len(data1)))
        self.assertTrue(values[n] > 0, 'Ma计算值前{}个应为大于零。'.format(n + 1))

    def test_QA_indicator_diff(self):
        n = 1
        count = 100
        data = pd.Series(np.arange(count))
        values = QA.DIFF(data, n)
        data1 = pd.Series(np.arange(n))
        data1 = data1.apply(lambda x: pd.np.nan)
        print('{}\n{}'.format(values[:n], data1))
        self.assertTrue(values[:n].equals(data1),
                        'Ma计算值前{}个应为NaN。长度：{} ： {}'.format(n, len(values[:n - 1]), len(data1)))

        n = 10
        data = pd.Series(np.arange(count))
        values = QA.DIFF(data, n)
        data1 = pd.Series(np.arange(n))
        data1 = data1.apply(lambda x: pd.np.nan)
        self.assertTrue(values[:n].equals(data1),
                        'Ma计算值前{}个应为NaN。长度：{} ： {}'.format(n, len(values[:n - 1]), len(data1)))
        data1 = pd.Series(np.arange(count))
        data1 = data1.apply(lambda x: n)
        self.assertTrue(values[n] == (data1[n]),
                        'Ma计算值前{}个应为NaN。\n{}\n{}\n长度：{} ： {}'.format(n, values[n:], data1[n:], len(values[n:]),
                                                                     len(data1[n:])))
