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

HEADERS = [ "Description",
            "Model Version",
            "ROI",
            "Stock-Hold Day",
            "Weekly Risk",
            "Trade Count",
            "Test Time"]

class BenchMarkRecorder():
    
    def __init__(self, model_infos):
        self.model_infos = model_infos
        self.rois = []
        self.hold_stock = []
        self.week_risks = []
        self.trade_count = [] 

    def update(self, result):
        self.rois.append(result["ROI"]/100+1)
        self.hold_stock.append(result["Stock-Hold Day"])
        self.week_risks.append(result["Weekly Risk"])
        self.trade_count.append(result["Trade Count"])

    def record(self, test_year):
        if not isdir(BENCHMARK_PATH):
            os.mkdir(BENCHMARK_PATH)
        filename = join(BENCHMARK_PATH, str(test_year)+'.csv')
        newFileFlag = True if not isfile(filename) else False
        
        fo = open(filename, 'ab')
        cw = csv.writer(fo, quoting=csv.QUOTE_ALL)

        if newFileFlag: cw.writerow(HEADERS)

        cw.writerow([self.model_infos["Model Description"],
                     self.model_infos["Model Version"],
                     str((gmean(self.rois)-1)*100)+'%' if len(self.rois) > 0 else '0.0%',
                     np.mean(self.hold_stock) if len(self.hold_stock) > 0 else 0.0,
                     np.mean(self.week_risks) if len(self.week_risks) > 0 else 0.0,
                     np.mean(self.trade_count) if len(self.trade_count) > 0 else 0.0,
                     datetime.strftime(datetime.now(),'%Y-%m-%d')
                    ])

        maxFactor = max(self.rois)
        minFactor = min(self.rois)

        print "Max: %f, Min: %f, Avg: %f, Gmean: %f, len: %d" % (maxFactor, minFactor, np.mean(self.rois), gmean(self.rois), len(self.rois))

        # distribution histagram

        binwidth = (maxFactor - minFactor)/100
        plt.hist(self.rois, bins=np.arange(minFactor, maxFactor + binwidth, binwidth))

        # set figure arguments
        fig = plt.gcf()
        fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

        # output figure
        if not isdir(BENCHMARK_DIST_PATH):
            os.mkdir(BENCHMARK_DIST_PATH)
        fig.savefig(BENCHMARK_DIST_PATH+self.model_infos["Model Description"]+str(test_year)+'.png', dpi=FIGURE_DPI)
        plt.clf()
        plt.close('all')
        