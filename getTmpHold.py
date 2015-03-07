#!/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import date
from ctrls.Tester import Tester
from models.exampleModel import exampleModel

def main():

    numbers = [ '1101', '0050' ]
    tester = Tester(numbers, exampleModel)
    tester.run( mode = 'tmpHold', dateFrom = date(2015,1,1))

if __name__ == '__main__':
    sys.exit(main())