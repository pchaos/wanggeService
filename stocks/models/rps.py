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
import datetime

import QUANTAXIS as qa
import numpy as np
import pandas as pd

from stocks.models import stockABS, Listing, convertToDate
from stocks.models import Stocktradedate

__author__ = 'pchaos'


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
            for v in Stocktradedate.get_real_datelisting(start, end).values('tradedate'):
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


class RPSprepare(RPSBase):
    """欧奈尔PRS预计算

    """

    class Meta:
        # app_label ='rps计算中间量'
        verbose_name = 'RPS准备'
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

    @classmethod
    def importStockListing(cls, start='2014-1-1'):
        """ 插入所有股票指
            qa.QA_fetch_stock_day_adv(v['code'], '1990-01-01', datetime.datetime.now().strftime("%Y-%m-%d"))
        执行 RPSprepare.importList('2013-12-25')，返回delisted count 628 :
        ['002231', '002343', '002360', '002410', '002534', '002653', '002672', '002680', '002693', '002822', '300084', '300172', '300239', '300252', '300264', '300363', '300454', '600028', '600103', '600115', '600238', '600252', '600326', '600365', '600409', '600410', '600415', '600416', '600418', '600420', '600422', '600423', '600425', '600426', '600428', '600432', '600433', '600435', '600436', '600438', '600439', '600446', '600449', '600452', '600456', '600458', '600459', '600460', '600461', '600463', '600466', '600467', '600468', '600469', '600470', '600475', '600477', '600478', '600479', '600480', '600481', '600482', '600483', '600485', '600486', '600487', '600488', '600489', '600490', '600491', '600493', '600495', '600496', '600497', '600498', '600499', '600500', '600501', '600502', '600503', '600505', '600507', '600508', '600509', '600510', '600511', '600512', '600513', '600516', '600517', '600518', '600519', '600521', '600522', '600523', '600525', '600526', '600527', '600528', '600529', '600530', '600531', '600532', '600533', '600535', '600536', '600537', '600540', '600543', '600545', '600546', '600547', '600548', '600549', '600551', '600552', '600557', '600558', '600559', '600561', '600562', '600563', '600565', '600566', '600567', '600568', '600570', '600571', '600572', '600573', '600575', '600576', '600577', '600578', '600580', '600581', '600582', '600583', '600584', '600586', '600587', '600588', '600589', '600590', '600592', '600593', '600594', '600595', '600596', '600597', '600598', '600599', '600600', '600601', '600602', '600603', '600604', '600605', '600606', '600610', '600611', '600612', '600613', '600614', '600616', '600617', '600618', '600619', '600621', '600623', '600624', '600626', '600628', '600630', '600633', '600634', '600635', '600637', '600638', '600639', '600640', '600641', '600642', '600643', '600644', '600647', '600648', '600649', '600650', '600652', '600654', '600655', '600657', '600658', '600660', '600661', '600662', '600663', '600664', '600665', '600666', '600667', '600668', '600673', '600674', '600675', '600676', '600677', '600682', '600683', '600684', '600685', '600686', '600687', '600688', '600690', '600691', '600693', '600694', '600697', '600699', '600701', '600703', '600704', '600705', '600708', '600710', '600711', '600712', '600713', '600715', '600717', '600718', '600719', '600720', '600723', '600724', '600725', '600728', '600730', '600732', '600735', '600736', '600738', '600739', '600741', '600742', '600743', '600748', '600749', '600750', '600751', '600755', '600757', '600758', '600759', '600763', '600764', '600765', '600770', '600773', '600774', '600775', '600776', '600777', '600780', '600782', '600783', '600784', '600785', '600787', '600789', '600790', '600791', '600792', '600794', '600795', '600796', '600797', '600798', '600803', '600804', '600805', '600807', '600811', '600812', '600814', '600816', '600818', '600819', '600820', '600823', '600824', '600825', '600826', '600827', '600828', '600829', '600830', '600831', '600833', '600834', '600835', '600836', '600837', '600838', '600839', '600841', '600845', '600846', '600850', '600851', '600853', '600856', '600857', '600858', '600861', '600862', '600863', '600864', '600865', '600868', '600869', '600871', '600873', '600874', '600879', '600880', '600882', '600884', '600885', '600886', '600888', '600889', '600891', '600892', '600893', '600894', '600895', '600896', '600898', '600900', '600908', '600909', '600917', '600919', '600926', '600936', '600958', '600959', '600960', '600962', '600963', '600965', '600966', '600969', '600970', '600973', '600975', '600976', '600977', '600978', '600979', '600981', '600982', '600983', '600986', '600987', '600988', '600990', '600992', '600993', '600995', '600996', '600998', '600999', '601000', '601002', '601003', '601007', '601008', '601009', '601010', '601011', '601016', '601018', '601020', '601038', '601058', '601069', '601099', '601106', '601107', '601113', '601116', '601118', '601126', '601128', '601137', '601155', '601158', '601163', '601166', '601168', '601169', '601177', '601179', '601188', '601198', '601208', '601211', '601212', '601216', '601218', '601228', '601229', '601233', '601258', '601288', '601326', '601328', '601339', '601360', '601366', '601368', '601369', '601375', '601377', '601388', '601390', '601398', '601500', '601515', '601518', '601519', '601555', '601567', '601588', '601595', '601599', '601608', '601616', '601618', '601628', '601633', '601668', '601669', '601677', '601678', '601688', '601700', '601717', '601718', '601727', '601766', '601788', '601789', '601798', '601800', '601801', '601808', '601818', '601857', '601858', '601881', '601882', '601899', '601900', '601901', '601928', '601929', '601958', '601966', '601969', '601988', '601989', '601991', '601992', '601996', '601997', '601998', '601999', '603000', '603001', '603002', '603005', '603006', '603007', '603009', '603011', '603012', '603015', '603016', '603017', '603018', '603021', '603022', '603023', '603025', '603026', '603028', '603029', '603030', '603031', '603032', '603035', '603038', '603039', '603040', '603066', '603069', '603077', '603088', '603089', '603090', '603098', '603099', '603101', '603108', '603118', '603123', '603128', '603131', '603157', '603158', '603165', '603179', '603188', '603189', '603197', '603203', '603208', '603226', '603239', '603258', '603298', '603300', '603309', '603315', '603318', '603319', '603330', '603333', '603337', '603355', '603358', '603360', '603388', '603399', '603421', '603456', '603508', '603515', '603518', '603519', '603520', '603528', '603535', '603536', '603558', '603559', '603567', '603568', '603588', '603598', '603599', '603600', '603606', '603611', '603618', '603633', '603636', '603656', '603660', '603667', '603669', '603677', '603690', '603699', '603701', '603703', '603708', '603716', '603726', '603729', '603730', '603737', '603738', '603766', '603767', '603779', '603788', '603799', '603800', '603801', '603806', '603818', '603823', '603838', '603843', '603861', '603866', '603869', '603878', '603888', '603889', '603899', '603901', '603908', '603918', '603933', '603936', '603939', '603958', '603959', '603960', '603966', '603969', '603978', '603979', '603986', '603987', '603988', '603989', '603993', '603996', '603997', '603998']

        :return:
        """
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
            for v in codelist.values()[20:100]:
                print('Dealing {} {} {}'.format(format(v['id'], '05d'), v['code'], v['name']))
                try:
                    # get stockcode
                    code = Listing.objects.get(code=v['code'], category=10)
                    # 本地获取指数日线数据
                    data = qa.QA_fetch_stock_day_adv(v['code'], realStart, datetime.datetime.now().strftime("%Y-%m-%d")).to_qfq()
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
                        df['tradedate'] = df['tradedate'].apply(lambda x: convertToDate(str(x)[:10])).astype(datetime.date)
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

            with transaction.atomic():
                for val in qssaved:
                    # 更新日期在原来保存区间的数据
                    val.index = pd.RangeIndex(len(val.index))
                    for ind in val.index:
                        v = val.iloc[ind]
                        rps = cls.objects.get(tradedate=val['tradedate'][0], code_id=v['code_id'])
                        rps.rps120 = v['rps120']
                        rps.rps250 = v['rps250']
                        rps.save()

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
        qs = cls.getlist('stock').filter(tradedate__gte=start, code_id=code_id)
        if qs.count() > 0:
            q = qs.values('tradedate', 'rps120', 'rps250', 'code_id')
            df2 = pd.DataFrame.from_records(q)
            df2['rps120'] = df2['rps120'].apply(lambda x: float(x)).astype(float)
            df2['rps250'] = df2['rps250'].apply(lambda x: float(x)).astype(float)
            df = cls.dfNotInAnotherdf(df, df2)
            # print(df)

        return df[~(df['tradedate'] <=df2['tradedate'].max()) & (df['tradedate'] >=df2['tradedate'].min())], \
               df[(df['tradedate'] <=df2['tradedate'].max()) & (df['tradedate'] >=df2['tradedate'].min())]

