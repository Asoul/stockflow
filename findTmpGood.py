#!/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import date
from ctrls.Tester import Tester
from models.exampleModel import exampleModel

def main():

    numbers = [ line.strip() for line in open('stocknumber.csv', 'rb') ]
    tester = Tester(numbers, exampleModel)
    tester.run( mode = 'tmpGood', dateFrom = date(2015,1,1), roiThr = -100)

if __name__ == '__main__':
    sys.exit(main())