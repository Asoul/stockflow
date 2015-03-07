#!/bin/python
# -*- coding: utf-8 -*-

'''基本範例格式'''

import sys
from ctrls.Tester import Tester
from models.exampleModel import exampleModel

def main():
    
    numbers = ['0050']# 股票編號
    tester = Tester(numbers, exampleModel)# 使用測試元件
    tester.run()# 模擬

if __name__ == '__main__':
    sys.exit(main())
