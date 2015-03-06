#!/bin/python
# -*- coding: utf-8 -*-

'''可以測試一個 Model 在特定的清單中歷年表現如何'''

import sys
from ctrls import *
from datetime import date
from ctrls.config import *
from models.exampleModel import exampleModel

number_list = [ line.strip() for line in open('stocknumber.csv', 'rb') ]

for test_year in xrange(BENCHMARK_YEAR_START, date.today().year-1911):

    variables = exampleModel().infos["Recommend Variables"]

    # 讀取該 model 可以用的參數們
    for variable in variables:

        br = BenchMarkRecorder(exampleModel(variable).infos)

        for number in number_list:
            sys.stdout.write('%4d  %s' % (test_year,number))

            reader = Reader(number)
            model = exampleModel(variable)

            trader = Trader(model.infos, number)#參數是Model Description 和 number

            while True:
                row = reader.getInput()
                if row == None: break
                
                model.update(row)
                prediction = model.predict()

                data_year = int(row[0].split('/')[0])
                if data_year > test_year: break
                elif data_year == test_year:
                    trade = trader.do(float(row[6]), prediction)
            
            result = trader.analysis()
            sys.stdout.write('  %4.3f %%\n' % result["ROI"])
            br.update(result)

        br.record(test_year)
