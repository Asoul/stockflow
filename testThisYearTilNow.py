#!/bin/python
# -*- coding: utf-8 -*-

'''測試 Model 對特定股票從今年年初跑到現在的結果'''

import sys
from datetime import date
from ctrls.Tester import Tester
from models.exampleModel import exampleModel

def main():

    numbers = ['1101']# 股票編號
    tester = Tester(numbers, exampleModel)# 使用測試元件
    tester.run(dateFrom = date(2015,1,1))# 模擬

if __name__ == '__main__':
    sys.exit(main())
