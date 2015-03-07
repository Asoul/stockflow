#!/bin/python
# -*- coding: utf-8 -*-

import sys
from ctrls.CandleDrawer import CandleDrawer

def main():

    candleDrawer = CandleDrawer()
    candleDrawer.draw('1101')

if __name__ == '__main__':
    sys.exit(main())