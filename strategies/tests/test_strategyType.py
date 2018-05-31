# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_strategyType.py

Description :

@Author :       pchaos

date：          18-5-2
-------------------------------------------------
Change Activity:
               18-5-2:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from strategies.models import StrategyType

__author__ = 'pchaos'


class TestStrategyType(TestCase):
    def test_baseStrategyType(self):
        """
        SQLite 不会强制检查字符长度，最长可保存500字符
        SQLite does not enforce the length of a VARCHAR.
        What is the maximum size of a VARCHAR in SQLite?

        SQLite does not enforce the length of a VARCHAR. You can declare a VARCHAR(10) and SQLite will be happy to let you put 500 characters in it. And it will keep all 500 characters intact - it never truncates.

        If you update the database using the django admin or model forms, Django will do the length validation for you. In the shell, you could manually call full_clean before saving, and catch the validation error.

        hz2Num = Foo(myAction="more than 1 char")
        try:
            hz2Num.full_clean()
            hz2Num.save()
        except ValidationError as e:
            # Do something based on the errors contained in e.message_dict.
        :return:
        """
        oldcount = StrategyType.objects.all().count()
        code = 'test01'
        name = 'testStrategyType  name 01'
        remark = 'test remarks'
        strategytype = StrategyType(code=code, name=name, remark=remark)
        strategytype.save()
        self.assertTrue(strategytype.code == code, '{} <!= {}'.format(strategytype.code, code))
        self.assertTrue(strategytype.name == name, '{} <!= {}'.format(strategytype.name, name))
        self.assertTrue(strategytype.remark == remark, '{} <!= {}'.format(strategytype.remark, remark))
        self.assertTrue(StrategyType.objects.all().count() > oldcount, 'StrategyType.objects.all().count() not great than old counts: {} > {}'.format(StrategyType.objects.all().count(), oldcount))
        strategytype = None
        strategytype = StrategyType.objects.get(code=code)
        self.assertTrue(strategytype.code == code, '{} <!= {}'.format(strategytype.code, code))
        print(strategytype)
        print('strategytype.name length: {}'.format(len(strategytype.name)))
        self.assertTrue(strategytype.name == name, '{} <!= {}'.format(strategytype.name, name))
        self.assertTrue(strategytype.remark == remark, '{} <!= {}'.format(strategytype.remark, remark))

        # no remark
        strategytype = StrategyType(code=code, name=name)
        self.assertTrue(strategytype.code == code, '{} <!= {}'.format(strategytype.code, code))
        self.assertTrue(strategytype.name == name, '{} <!= {}'.format(strategytype.name, name))
        self.assertTrue(strategytype.remark == '', '{} <!= {}'.format(strategytype.remark, ''))
