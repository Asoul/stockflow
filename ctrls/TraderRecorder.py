#!/bin/python
# -*- coding: utf-8 -*-

import os
import csv
from config import *
from datetime import datetime
import matplotlib.pyplot as plt
from os.path import isfile, join, isdir

HEADERS = [ 
    "Description",
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
    "Test Time"
]

class TraderRecorder():
    '''Record the Trader result'''

    def getFromattedTime(self):
        '''回傳現在格式化的時間，ex. 2015/03/06 17:25:16 '''
        t = datetime.now()
        return (str(t.year)+'/'+str(t.month).zfill(2)+'/'+'/'+str(t.day).zfill(2)+'/'+
            str(t.hour).zfill(2)+':'+str(t.minute).zfill(2)+':'+str(t.second).zfill(2))

    def recordToCSV(self, folder, filename, col1, row):
        ''' 把資料存到紀錄同一個 Model 資料、和同一隻股票資料的檔案中
        folder 是輸出位置：有可能是 MODEL_RESULT_PATH 或 STOCK_RESULT_PATH 
        filename 是檔案名稱：如果是 Model 的話就是 Model 的敘述，Stock 的話就是股票編號
        col1 是紀錄首欄的位置：存到同一 Model 的檔案中會記的是不懂的股票編號，同一 Stock 下會記的是不同 Model 的敘述
        '''
        newFileFlag = True if not isfile(join(folder, filename+'.csv')) else False

        fo = open(join(folder, filename+'.csv'), 'ab')
        cw = csv.writer(fo, quoting=csv.QUOTE_ALL)

        if newFileFlag: cw.writerow(HEADERS)

        cw.writerow([col1]+row)

    def recordToPNG(self, result):
        '''輸出買賣過程的圖檔，紅色的三角形是買入，藍色正方形是賣出'''
        # 輸出買賣圖檔
        x_axis = range(len(result["Value Series"]))
        
        plt.plot(x_axis, result["Value Series"], c='#000000', ls='-', lw=0.2)
        plt.plot(x_axis, result["Buy Series"], c='#ff0000', marker='o', ms=5, alpha=0.5)
        plt.plot(x_axis, result["Sell Series"], c='#0000ff', marker='s', ms=5, alpha=0.5)

        plt.title('ROI = '+str(result["ROI"])+'%, ROI/Trade = '+str(result["ROI Per Trade"])+'%')

        # set figure arguments
        fig = plt.gcf()
        fig.set_size_inches(FIGURE_WIDTH, FIGURE_HEIGHT)

        # 存到同一隻 Model 下
        
        if not isdir(join(MODEL_FIGURE_PATH, result["Model Description"])):
            os.mkdir(join(MODEL_FIGURE_PATH, result["Model Description"]))
        fig.savefig(join(MODEL_FIGURE_PATH, result["Model Description"], result["Stock Number"]+'.png'), dpi=FIGURE_DPI)

        # 存到同一隻 Stock 下
        
        if not isdir(join(STOCK_FIGURE_PATH, result["Stock Number"])):
            os.mkdir(join(STOCK_FIGURE_PATH, result["Stock Number"]))
        fig.savefig(join(STOCK_FIGURE_PATH, result["Stock Number"], result["Model Description"]+'.png'), dpi=FIGURE_DPI)
        
        plt.clf()
        plt.close('all')
        
    def record(self, result, noCSV = False, noPNG = False):
        '''把 Treader 的結果記錄下來'''
        row = [
            str(result["ROI"])+'%',
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
            self.getFromattedTime()
        ]

        if not noCSV:
            self.recordToCSV(MODEL_RESULT_PATH, result["Model Description"], result["Stock Number"], row)
            self.recordToCSV(STOCK_RESULT_PATH, result["Stock Number"], result["Model Description"], row)

        if not noPNG:
            self.recordToPNG(result)
