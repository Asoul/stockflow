#!/bin/python
# -*- coding: utf-8 -*-

'''基本範例格式'''

import sys
from ctrls.Tester import Tester
from models.exampleModel import exampleModel

def main():
    
    numbers = ['1314']# 股票編號

    tester = Tester(numbers, exampleModel)

    tester.train(noLog = False, noRecord = True)


if __name__ == '__main__':
    sys.exit(main())
