# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@File    : test_wangge.py
Description :
@Author :       pchaos
date：          18-4-1
-------------------------------------------------
Change Activity:
               18-4-1:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from unittest import TestCase
from WANGGE.wangge import *


__author__ = 'pchaos'


class TestWangge(TestCase):
    def setUp(self):
        self.high = 100.0
        self.low = 0.0
        self.n = 20  # 网格为20格
        # self.wg = wangGebase(self.high, self.low, self.n)
        self.wg = simpleWange(self.high, self.low, self.n)

    def tearDown(self):
        self.wg = None

    def test_doCaculateSimpleWangge(self):
        wangge = self.wg()
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.high = 1.323
        self.low = 0.414
        wangge = self.wg(self.high, self.low, self.n)
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.n = 30
        wangge = self.wg(self.high, self.low, self.n)
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.n = 40
        wangge = self.wg(self.high, self.low, self.n)
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.assertTrue(self.isequal(wangge[0][1], self.high), "计算错误，计算结果和实际网格最大值不相等: {0} != {1}".format(wangge[0][1], self.high))

    def test_doCaculateROExWangge(self):
        """
        价格等比变化
        :return:
        """
        self.high = 20.0
        self.low = 10.0
        self.n = 20  # 网格为20格
        # self.wg = wangGebase(self.high, self.low, self.n)
        self.wg = ROEWangge(self.high, self.low, self.n)
        wangge = self.wg()
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.assertTrue(self.isequal(wangge[0][1], self.high), "计算错误，计算结果和实际网格最大值不相等: {0} != {1}".format(wangge[0][1], self.high))
        self.assertTrue(wangge[self.n // 2][1] < (self.high + self.low) / 2,
                        "计算错误，计算结果和实际网格中间值: {0} < {1}".format(wangge[self.n // 2][1], (self.high + self.low) / 2))

        self.high = 1.323
        self.low = 0.414
        self.n = 39  # 网格为39格
        # self.wg = wangGebase(self.high, self.low, self.n)
        self.wg = ROEWangge(self.high, self.low, self.n)
        wangge = self.wg()
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.assertTrue(self.isequal(wangge[0][1], self.high), "计算错误，计算结果和实际网格最大值不相等: {0} != {1}".format(wangge[0][1], self.high))

        self.high = 1.323
        self.low = 0.414
        self.n = 40  # 网格为40格
        # self.wg = wangGebase(self.high, self.low, self.n)
        self.wg = ROEWangge(self.high, self.low, self.n)
        wangge = self.wg()
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.assertTrue(self.isequal(wangge[0][1], self.high), "计算错误，计算结果和实际网格最大值不相等: {0} != {1}".format(wangge[0][1], self.high))

        # 603180 2018 05 05
        self.high = np.round(179.9*1.015, 2)
        self.low = np.round(133.53*0.985, 2)
        # self.low = np.round(self.high * 0.75, 2)
        self.n = 11  # 网格为11格
        adp = 3 # 计算结果保留3位小数
        # self.wg = wangGebase(self.high, self.low, self.n)
        self.wg = ROEWangge(self.high, self.low, self.n, adp)
        wangge = self.wg()
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low, diff=0.001), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.assertTrue(self.isequal(wangge[0][1], self.high, diff= 0.001), "计算错误，计算结果和实际网格最大值不相等: {0} != {1}".format(wangge[0][1], self.high))

    def isequal(self, value1, value2, diff = 0.0001):
        """
        比较两个值的差是否在diff区间内
        :param value1: 值一
        :param value2: 值二
        :param diff: 相差范围
        :return: 两个值的差在diff范围内，True
                 两个值的差不在diff范围内，False
        """
        return np.abs(value1 - value2) < diff
