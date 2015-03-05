#!/bin/python
# -*- coding: utf-8 -*-

import os
import csv
from config import *
from datetime import datetime
import matplotlib.pyplot as plt
from os.path import isfile, join, isdir

HEADERS = [ "Description",
            "ROI",
            "ROI Per Trade",
            "Weekly ROI",
            "Daily Risk",
            "Weekly Risk",
            "Monthly Risk",
            "Yearly Risk",
            "Buy Count",
            "Sell Count",
            "Trade Count",
            "Stock / Asset Rate",
            "Stock / Asset Change Std",
            "Stock-Hold Day",
            "Initial Money",
            "Update Time",
            "Model Version",
            "Test Time"]

class TraderRecorder():
    '''Record the Trader result'''
    def recordToStock(self, result):# 輸出至同一個 Stock 之下

        newFileFlag = True if not isfile(join(STOCK_RESULT_PATH, result["Stock Number"])) else False

        if not isdir(STOCK_RESULT_PATH):
            os.mkdir(STOCK_RESULT_PATH)

        fo = open(join(STOCK_RESULT_PATH, result["Stock Number"]+'.csv'), 'ab')
        cw = csv.writer(fo, quoting=csv.QUOTE_ALL)

        if newFileFlag:
            cw.writerow(HEADERS)        
        
        cw.writerow([result["Model Description"]] + self.row)

    def recordToModel(self, result):# 輸出至同一個 Model 之下

        newFileFlag = True if not isfile(join(MODEL_RESULT_PATH, result["Model Description"]+'.csv')) else False

        if not isdir(MODEL_RESULT_PATH):
            os.mkdir(MODEL_RESULT_PATH)

        fo = open(join(MODEL_RESULT_PATH, result["Model Description"]+'.csv'), 'ab')
        cw = csv.writer(fo, quoting=csv.QUOTE_ALL)

        if newFileFlag:
            cw.writerow(HEADERS)

        cw.writerow([result["Stock Number"]]+self.row)

    def record(self, result):

        self.row = [str(result["ROI"])+'%',
                    str(result["ROI Per Trade"])+'%',
                    str(result["Weekly ROI"])+'%',
                    result["Daily Risk"],
                    result["Weekly Risk"],
                    result["Monthly Risk"],
                    result["Yearly Risk"],
                    result["Buy Count"],
                    result["Sell Count"],
                    result["Trade Count"],
                    result["Stock / Asset Rate"],
                    result["Stock / Asset Change Std"],
                    result["Stock-Hold Day"],
                    result["Initial Money"],
                    result["Update Time"],
                    result["Model Version"],
                    datetime.strftime(datetime.now(),'%Y-%m-%d')
                    ]

        self.recordToStock(result)
        self.recordToModel(result)
        

        # 輸出買賣圖檔

        x_axis = range(0, len(result["Series"]))
        plt.plot(x_axis, result["Series"], c='#000000', ls='-', lw=0.2)
        plt.plot(x_axis, result["Buy Series"], c='#ff0000', marker='o', ms=5, alpha=0.5)
        plt.plot(x_axis, result["Sell Series"], c='#0000ff', marker='s', ms=5, alpha=0.5)
        plt.title('ROI = '+str(result["ROI"])+'%, ROI/Trade = '+str(result["ROI Per Trade"])+'%')

        # set figure arguments
        fig = plt.gcf()
        fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

        # output figure
        # 存到同一隻 Model 下
        if not isdir(MODEL_FIGURE_PATH):
            os.mkdir(MODEL_FIGURE_PATH)
        if not isdir(join(MODEL_FIGURE_PATH, result["Model Description"])):
            os.mkdir(join(MODEL_FIGURE_PATH, result["Model Description"]))
        fig.savefig(join(MODEL_FIGURE_PATH, result["Model Description"], result["Stock Number"][:-4]+'.png'), dpi=FIGURE_DPI)

        # 存到同一隻 Stock 下
        if not isdir(STOCK_FIGURE_PATH):
            os.mkdir(STOCK_FIGURE_PATH)
        if not isdir(join(STOCK_FIGURE_PATH, result["Stock Number"][:-4])):
            os.mkdir(join(STOCK_FIGURE_PATH, result["Stock Number"][:-4]))
        fig.savefig(join(STOCK_FIGURE_PATH, result["Stock Number"][:-4], result["Model Description"]+'.png'), dpi=FIGURE_DPI)
        
        plt.clf()
        plt.close('all')
        