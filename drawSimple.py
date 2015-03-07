#!/bin/python
# -*- coding: utf-8 -*-

import sys
from ctrls.SimpleDrawer import SimpleDrawer

def main():

    simpleDrawer = SimpleDrawer()
    simpleDrawer.draw('1101')

if __name__ == '__main__':
    sys.exit(main())