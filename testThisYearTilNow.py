#!/bin/python
# -*- coding: utf-8 -*-

'''測試 Model 對特定股票從今年年初跑到現在的結果'''

import sys
from ctrls import *
from models.exampleModel import exampleModel

def main():

    number_list = [ "2488" ]

    variables = exampleModel().infos["Recommend Variables"]

    for variable in variables:

        for number in number_list:

            model = exampleModel(variable)
            reader = Reader(number)

            trader = Trader(model.infos, number)#參數是Model Description 和 number

            while True:
                
                row = reader.getInput()
                if row == None: break

                model.update(row)
                prediction = model.predict()
                
                data_year = row[0].split('/')[0]
                if data_year == '104':
                    trader.do(float(row[6]), prediction)
                    # if trade[5] != 0: print trade

            result = trader.analysis()
            sys.stdout.write('%s\t\t%.3f %%\n' % (number, result["ROI"]))
            

if __name__ == '__main__':
    sys.exit(main())
