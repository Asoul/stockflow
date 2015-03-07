#!/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
from config import *
from datetime import datetime
import matplotlib.pyplot as plt
from os.path import isfile, join, isdir
from scipy.stats.mstats import gmean

HEADERS = [ 
    "Description",
    "Model Version",
    "ROI",
    "Stock-Hold Day",
    "Weekly Risk",
    "Trade Count",
    "Test Time"
]

class BenchYearRecorder():
    '''Record the BenchMark Result For Year'''
    def __init__(self, model_infos, year):
        self.model_infos = model_infos
        self.rois = []
        self.hold_stock = []
        self.week_risks = []
        self.trade_count = [] 
        self.year = year

    def _getFromattedTime(self):
        '''回傳現在格式化的時間，ex. 2015/03/06 17:25:16 '''
        t = datetime.now()
        return (str(t.year)+'/'+str(t.month).zfill(2)+'/'+'/'+str(t.day).zfill(2)+'/'+
            str(t.hour).zfill(2)+':'+str(t.minute).zfill(2)+':'+str(t.second).zfill(2))

    def update(self, result):
        self.rois.append(result["ROI"]/100+1)
        self.hold_stock.append(result["Stock-Hold Day"])
        self.week_risks.append(result["Weekly Risk"])
        self.trade_count.append(result["Trade Count"])

    def record(self):
        
        filename = join(BENCHMARK_YEAR_PATH, str(self.year)+'.csv')
        newFileFlag = True if not isfile(filename) else False
        
        fo = open(filename, 'ab')
        cw = csv.writer(fo, quoting=csv.QUOTE_ALL)

        if newFileFlag: cw.writerow(HEADERS)

        cw.writerow([
            self.model_infos["Model Description"],
            self.model_infos["Model Version"],
            str(round((gmean(self.rois)-1)*100, 3))+'%' if len(self.rois) > 0 else '0.0%',
            round(np.mean(self.hold_stock), 3) if len(self.hold_stock) > 0 else 0.0,
            round(np.mean(self.week_risks), 3) if len(self.week_risks) > 0 else 0.0,
            round(np.mean(self.trade_count), 3) if len(self.trade_count) > 0 else 0.0,
            self._getFromattedTime()
        ])
        