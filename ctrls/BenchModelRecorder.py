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

class BenchModelRecorder():
    '''Record the BenchMark Result For Model'''
    def __init__(self, model_infos, number):
        self.model_description = model_infos["Model Description"]
        self.number = number
        self.rois = []
        self.total_roi = 1.0

    def _getModelHeader(self):
        '''輸出至同一個 Model 下紀錄的 Header'''
        header = ["number"]
        for year in range(BENCHMARK_YEAR_START, BENCHMARK_YEAR_END + 1):
            header.append(year)
        header.append('total')
        return header

    def update(self, result):
        self.rois.append(str(round(result["ROI"], 3)) + '%')
        self.total_roi *= (result["ROI"]/100+1)

    def record(self):
        
        filename = join(BENCHMARK_MODEL_PATH, self.model_description + '.csv')
        newFileFlag = True if not isfile(filename) else False

        f = open(filename, 'ab')
        cw = csv.writer(f, delimiter = ',')

        if newFileFlag: cw.writerow(self._getModelHeader())

        cw.writerow([self.number] + self.rois + [str(round((self.total_roi-1)*100, 3)) + '%'])

        self.rois = []
        self.total_roi = 1.0
