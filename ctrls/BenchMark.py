#!/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
from ctrls import *
from settings import *
from os import listdir
from os.path import isfile, join

class BenchMark():
    '''To Run BenchMark on specific numbers for specific years'''

    def __init__(self, numbers, Model):
        # check the number from Database, remove error numbers
        tsecNumbers = [ n[:-4] for n in listdir(TSEC_DATA_PATH) if n[-4:] == '.csv' ]
        for number in numbers:
            if number not in tsecNumbers:
                numbers.remove(number)

        self.numbers = numbers
        self.Model = Model
        self.years = range(BENCHMARK_YEAR_START, BENCHMARK_YEAR_END + 1)

    def getROI(self, result):
        if len(result["Asset Series"]) > 0:
            return str(round((float(result["Asset Series"][-1])/result["Asset Series"][0] - 1)*100, 3)) + '%'
        else:
            return "0.000 %"

    def dailyUpdate(self, model, trader, row):
        trader.updateData(row)

        # 開盤的買：用開盤價交易
        order = model.predict('start', float(row[3]))
        trade = trader.place('start', order)
        model.updateTrade(trade)

        # 開盤後，盤中掛單
        order = model.predict('mid', float(row[3]))
        trade = trader.place('mid', order)
        model.updateTrade(trade)

        # 盤末的更新
        model.updateData(row)

        # 收盤的買：用收盤價交易
        order = model.predict('end', float(row[6]))
        trade = trader.place('end', order)
        model.updateTrade(trade)

    def run(self, noLog = False):
        '''
            依照年份測試指定清單的資料。
        '''
        # Initialize BenchYearRecorder and BenchModelRecorder
        benchYearRecorders = dict()
        BenchModelRecorder(self.Model().infos, '0000').restart()
        for year in self.years:
            benchYearRecorders[year] = BenchYearRecorder(self.Model().infos, year)

        for number in self.numbers:

            benchModelRecorder = BenchModelRecorder(self.Model().infos, number)

            for year in self.years:

                if not noLog: sys.stdout.write('%s  %4d' % (number, year))

                reader = Reader(number)
                model = self.Model()
                trader = Trader(model.infos, number, True)

                while True:

                    row = reader.getInput()
                    if row == None: break

                    data_year = int(row[0].split('/')[0])

                    if data_year > year: break
                    elif data_year == year:
                        self.dailyUpdate(model, trader, row)
                    else:
                        model.updateData(row)

                result = trader.getResult()

                if not noLog: sys.stdout.write('\t%s\n' % self.getROI(result))

                benchYearRecorders[year].update(result)
                benchModelRecorder.update(result)

            meta_model = self.Model()
            meta_trader = Trader(self.Model().infos, number, True)
            reader = Reader(number)
            while True:
                row = reader.getInput()
                if row == None: break
                        
                self.dailyUpdate(meta_model, meta_trader, row)
            result = meta_trader.getResult()
            if not noLog: sys.stdout.write('all\t%s\n' % self.getROI(result))
            benchModelRecorder.updateFinal(result)
            benchModelRecorder.record()

        for year in self.years:
            benchYearRecorders[year].record()
