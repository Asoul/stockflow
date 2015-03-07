#!/bin/python
# -*- coding: utf-8 -*-

'''可以測試一個 Model 在特定的清單中歷年表現如何'''

import sys
from ctrls.BenchMark import BenchMark
from models.exampleModel import exampleModel

def main():
    
    number_list = [ line.strip() for line in open('stocknumber.csv', 'rb') ]
    benchmark = BenchMark(number_list, exampleModel)
    benchmark.run()

if __name__ == '__main__':
    sys.exit(main())