#!/usr/bin/bash

 # todo 在django shell里面不会执行main？？？
# echo $1
source ~/.bashrc
#  第一个参数传进来python环境名称
conda activate $1
python updateStockData.py
