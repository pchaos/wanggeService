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

        self.high = 200
        self.low = 144
        self.n = 13  # 网格为30格
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

        # 603180 2018 04 20
        self.high = 179.9
        self.low = np.round(self.high * 0.8, 2)
        self.n = 9  # 网格为8格
        # self.wg = wangGebase(self.high, self.low, self.n)
        self.wg = ROEWangge(self.high, self.low, self.n)
        wangge = self.wg()
        print(wangge)
        self.assertTrue(self.isequal(wangge[-1][1], self.low), "计算错误，计算结果和实际网格最小值不相等: {0} != {1}".format(wangge[-1][1], self.low))
        self.assertTrue(self.isequal(wangge[0][1], self.high), "计算错误，计算结果和实际网格最大值不相等: {0} != {1}".format(wangge[0][1], self.high))

    def isequal(self, value1, value2):
        return np.abs(value1 - value2) < 0.0001
