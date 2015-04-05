#!/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
from settings import *
from datetime import datetime
import matplotlib.pyplot as plt
from os.path import isfile, join, isdir
from scipy.stats.mstats import gmean
from scipy.stats import norm

HEADERS = [ 
    "Description",
    "Model Version",
    "ROI",
    "Stock-Hold Day",
    "Yearly Risk Mean",
    "Yearly Risk Std",
    "Positive Rate",
    "Trade Count",
    "Test Time"
]

class BenchYearRecorder():
    '''Record the BenchMark Result For Year'''
    def __init__(self, model_infos, year):
        self.model_infos = model_infos
        self.rois = []
        self.hold_stock = []
        self.risks = []
        self.trade_count = [] 
        self.year = year

    def _getFromattedTime(self):
        '''回傳現在格式化的時間，ex. 2015/03/06 17:25:16 '''
        t = datetime.now()
        return (str(t.year)+'/'+str(t.month).zfill(2)+'/'+'/'+str(t.day).zfill(2)+' '+
            str(t.hour).zfill(2)+':'+str(t.minute).zfill(2)+':'+str(t.second).zfill(2))

    def update(self, result, year_day):
        self.rois.append(float(result["Asset Series"][-1])/result["Asset Series"][-year_day])
        for i in range(-year_day + 1, 0):
            if float(result["Asset Series"][i])/result["Asset Series"][i-1] <= 0:
                print "Q_Q", float(result["Asset Series"][i])/result["Asset Series"][i-1]
                continue
            self.risks.append(np.log(float(result["Asset Series"][i])/result["Asset Series"][i-1]))
        
        if sum(result["Buyed Stock Series"][-year_day:]) > 0:
            self.hold_stock.append(float(sum(result["Stock Series"][-year_day:])) / \
                                         sum(result["Buyed Stock Series"][-year_day:]))
        else:
            self.hold_stock.append(0)
        
        self.trade_count.append(result["Trade Series"][-year_day:].count(1) + \
                                result["Trade Series"][-year_day:].count(-1))

    def formatRoundPercent(self, num):
        return str(round(num * 100, 3))+'%'

    def record(self):
        
        filename = join(BENCHMARK_YEAR_PATH, str(self.year)+'.csv')
        newFileFlag = True if not isfile(filename) else False
        
        fo = open(filename, 'ab')
        cw = csv.writer(fo, quoting=csv.QUOTE_ALL)

        if newFileFlag: cw.writerow(HEADERS)

        if len(self.rois) > 0:
            roi = np.mean(self.rois) - 1
            risk_avg = np.mean(self.risks)
            risk_std = np.std(self.risks)
            stock_hold_day = np.mean(self.hold_stock)
            positive_rate = 1.0 - norm.cdf(-risk_avg/risk_std)
            trade_count = np.mean(self.trade_count)
        else:
            roi = 0
            risk_avg = 0
            risk_std = 0
            stock_hold_day = 0
            positive_rate = 0
            trade_count = 0

        cw.writerow([
            self.model_infos["Model Description"],
            self.model_infos["Model Version"],
            self.formatRoundPercent(roi),
            round(stock_hold_day, 3),
            self.formatRoundPercent(risk_avg),
            self.formatRoundPercent(risk_std),
            self.formatRoundPercent(positive_rate),
            round(trade_count, 3),
            self._getFromattedTime()
        ])
        