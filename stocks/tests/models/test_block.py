# -*- coding: utf-8 -*-
"""
-------------------------------------------------

@File    : test_block.py

Description :

@Author :       pchaos

tradedate：          18-5-9
-------------------------------------------------
Change Activity:
               18-5-9:
@Contact : p19992003#gmail.com                   
-------------------------------------------------
"""
from django.test import TestCase
from stocks.models import Block, BlockDetail, Listing
from stocks.models import qa


__author__ = 'pchaos'


class TestBK(TestCase):
    def setUp(self):
        # qa.QA_util_log_info('Listing.importStockListing')
        # listing = Listing.importStockListing()
        # Listing.importIndexListing()
        # assert Listing.getlist('stock').count() > 2000
        # qa.QA_util_log_info('Block.initBlock')
        Block.initBlock()


    def test_TDX(self):
        """
        默认已经初始化板块名称：通达信 同花顺 自定义 其他
        """
        bkname = '通达信'
        bk = Block.objects.all().filter(name=bkname)
        self.assertTrue(bk is not None and bk[0].name == bkname, '未找到板块:{}'.format(bkname))
        bk = Block.objects.get(name=bkname)
        self.assertTrue(bk is not None and bk.name == bkname, '未找到板块:{}'.format(bkname))
        # 测试没有此板块，抛出异常
        bkname = '没有此板块'
        # self.assertRaises(TypeError, BK.objects.get(name=bkname), '未找到板块:{}'.format(bkname))
        with self.assertRaises(Exception) as context:
            bk = Block.objects.get(name=bkname)
        self.assertTrue('query does not exist.' in str(context.exception), '{}'.format(context.exception))

    def test_importTDXList(self):

        tdxblock = Block.importTDXList()
        print('tdxblock:{} \n{}'.format(tdxblock, tdxblock[0]))
        self.assertTrue(len(tdxblock) == 4, '通达信子类包含四类')
        tdxblocks = Block.getlist(tdxblock[0])
        print('tdxblocks {} : {}'.format(tdxblock[0], tdxblocks))
        self.assertTrue(len(tdxblocks) > 10, '版块数量应大于10： {}'.format(tdxblocks))
        # tdxdetail = BlockDetail.getlist(tdxblocks[0])
        tdxdetail = BlockDetail.getlist()
        self.assertTrue(len(tdxdetail) > 0, '版块数量应大于0： {} : {}'.format(tdxblocks[0], tdxdetail))

    def test_insertBlock(self):
        bkname = '自定义'
        bk = Block.objects.all().filter(name=bkname)
        newblockname = 'RPS'
        Block.objects.create(code='RPS', name=newblockname, parentblock=bk[0], remarks='RPS版块')
        bk = Block.objects.all().filter(name=newblockname)
        self.assertTrue(len(bk) == 1, '{} 未保存成功'.format(newblockname))
