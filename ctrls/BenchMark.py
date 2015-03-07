#!/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
from ctrls import *
from config import *
from os import listdir
from os.path import isfile, join

class BenchMark():
    '''To Run BenchMark on specific numbers for specific years'''

    def __init__(self, numbers, Model, years):
        # check the number from Database, remove error numbers
        tsecNumbers = [ n[:-4] for n in listdir(TSEC_DATA_PATH) if n[-4:] == '.csv' ]
        for number in numbers:
            if number not in tsecNumbers:
                numbers.remove(number)

        self.numbers = numbers
        self.Model = Model
        self.years = range(BENCHMARK_YEAR_START, BENCHMARK_YEAR_END + 1)

    def getModelHeader(self):
        '''輸出至同一個 Model 下紀錄的 Header'''
        header = ["number"]
        for year in self.years:
            self.HEADER.append(year)
        self.HEADER.append('total')
        
    def recordForModel(self, number, model_rois):
        '''紀錄至同一個 Model 下'''
        filename = join(BENCHMARK_MODEL_PATH, number + '.csv')
        newFileFlag = True if not isfile(filename) else False

        f = open(filename, 'ab')
        cw = csv.writer(f, delimiter = ',')

        if newFileFlag: cw.writerow(self.getModelHeader())

        cw.writerow(model_rois)

    def run(self):
        '''
            依照年份測試指定清單的資料。
        '''
        # Initialize BenchMarkRecorder
        brs = dict()
        for year in self.years:
            brs[year] = BenchMarkRecorder(self.Model().infos, year)

        for number in self.numbers:

            model_rois = [number]
            overall_roi = 1.0

            for year in self.years:

                sys.stdout.write('%4d  %s' % (year ,number))

                reader = Reader(number)
                model = self.Model()
                trader = Trader(model.infos, number)

                while True:

                    row = reader.getInput()
                    if row == None: break
                    
                    prediction = model.predict()
                    data_year = int(row[0].split('/')[0])

                    if data_year > year: break
                    elif data_year == year:
                        trade = trader.do(row, prediction)
                        model.update(row, trade)
                    else:
                        model.update(row, None)

                result = trader.analysis()

                sys.stdout.write('  %4.3f %%\n' % result["ROI"])

                brs[year].update(result)
                model_rois.append(str(round(result["ROI"], 3) + '%'))
                overall_roi *= result["ROI"]

            model_rois.append(overall_roi)
            self.recordForModel(number, model_rois)

        for year in self.years:
            brs[year].record()
