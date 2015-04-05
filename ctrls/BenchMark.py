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

    def getROI(self, result, finalFlag):
        if len(result["Asset Series"]) > 0:
            day = len(result["Asset Series"]) if finalFlag else min(260, len(result["Asset Series"]))
            return str(round((float(result["Asset Series"][-1])/result["Asset Series"][-day] - 1)*100, 3)) + '%'
        else:
            return "0.000 %"

    def run(self, noLog = False):
        '''
            依照年份測試指定清單的資料。
        '''
        # Initialize BenchYearRecorder and BenchModelRecorder
        benchYearRecorders = dict()
        BenchModelRecorder(self.Model().infos, '0000').restart()
        
        for year in self.years:
            benchYearRecorders[year] = BenchYearRecorder(self.Model().infos, year)
        benchYearRecorders['all'] = BenchYearRecorder(self.Model().infos, 'all')

        for number in self.numbers:

            benchModelRecorder = BenchModelRecorder(self.Model().infos, number)
            reader = Reader(number)
            model = self.Model()
            trader = Trader(model.infos, number, True)
            
            old_year = None
            year_day = 0
            
            while True:

                row = reader.getInput()
                if row == None:
                    result = trader.getResult()
                    benchModelRecorder.update(result, year_day)
                    benchYearRecorders[old_year].update(result, year_day)
                    break

                data_year = int(row[0].split('/')[0])
                year_day += 1

                if old_year != data_year and old_year:
                    result = trader.getResult()
                    benchModelRecorder.update(result, year_day)
                    benchYearRecorders[old_year].update(result, year_day)
                    year_day = 1

                    if not noLog:
                        sys.stdout.write('%s  %4d\t%s\n' % (number, old_year, self.getROI(result, False)))

                if data_year > year: break
                else:
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

                old_year = data_year
            
            if not noLog:
                sys.stdout.write('%s  all\t%s\n' % (number, self.getROI(result, True)))

            benchModelRecorder.updateFinal(result)
            benchModelRecorder.record()

            benchYearRecorders['all'].update(result, len(result["Asset Series"]))

        for year in self.years:
            benchYearRecorders[year].record()
        benchYearRecorders['all'].record()
