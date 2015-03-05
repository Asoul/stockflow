#!/bin/python
# -*- coding: utf-8 -*-

'''基本範例格式'''

import sys
from ctrls import *
from models.exampleModel import exampleModel

def main():
    
    number = '1314'# 股票編號

    reader = Reader(number)
    model = exampleModel()
    trader = Trader(model.infos, number)
    tr = TraderRecorder()
    
    while True:
        row = reader.getInput()
        if row == None: break

        model.update(row)

        prediction = model.predict()
        
        trade = trader.do(float(row[6]), prediction)
        if trade[5] != 0: print trade
    
    tr.record(trader.analysis())

if __name__ == '__main__':
    sys.exit(main())
