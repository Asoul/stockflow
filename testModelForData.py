#!/bin/python
# -*- coding: utf-8 -*-

import csv
import sys
from ctrls import *
from os import listdir
from datetime import date
from os.path import isfile
from ctrls.config import *
from models.exampleModel import exampleModel

last_year = date.today().year-1912

HEADER = ['Filename']
for i in range(TESTALLDATA_YEAR_START, last_year):
    HEADER.append(str(i))
HEADER.append(str(TESTALLDATA_YEAR_START)+'-'+str(last_year))

def main():

    number_list = [ f for f in listdir('tsec/data') if f[-4:] == '.csv' ]

    variables = exampleModel().infos["Recommend Variables"]

    model_name = 'exampleModel'
    filename = 'results/testalldata/'+model_name+'.csv' 

    newFileFlag = False if isfile(filename) else True

    fo = open(filename, 'ab')
    cw = csv.writer(open(filename, 'ab'), delimiter=',', quoting=csv.QUOTE_ALL)
    if newFileFlag:
        cw.writerow(HEADER)

    # 讀取該 model 可以用的參數們
    for variable in variables:

        for number in number_list:
            
            outputrow = [number[:-4]]
            over_all = 1.0

            model = exampleModel(variable)
            reader = Reader(number)
            haveOldDataFlag = False

            for test_year in range(TESTALLDATA_YEAR_START, last_year):

                sys.stdout.write('%s\t%4d' % (number, test_year))
                trader = Trader(model.infos, number)#參數是Model Description 和 number

                while True:

                    # 如果上次有資料就用，不用讀
                    if haveOldDataFlag:
                        haveOldDataFlag = False
                    else:
                        row = reader.getInput()
                    
                    if row == None: break

                    data_year = int(row[0].split('/')[0])

                    if data_year > test_year:
                        haveOldDataFlag = True
                        break

                    elif data_year == test_year:
                        model.update(row)
                        prediction = model.predict()
                        trade = trader.do(float(row[6]), prediction)

                result = trader.analysis()
                sys.stdout.write('\t\t%.3f %%\n' % result["ROI"])
                over_all *= (result["ROI"]/100.0+1.0)
                outputrow.append(str(result["ROI"])+'%')
            
            outputrow.append(str((over_all-1.0)*100.0)+'%')
            cw.writerow(outputrow)
            
            sys.stdout.write('%s\toverall\t\t%.3f %%\n' % (number, (over_all-1)*100))

if __name__ == '__main__':
    sys.exit(main())
