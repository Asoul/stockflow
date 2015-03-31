#!/bin/python
# -*- coding: utf-8 -*-

import os
import csv
from settings import *
from datetime import datetime
import matplotlib.pyplot as plt
from os.path import isfile, join, isdir

HEADERS = [ 
    "Description",
    "ROI",
    "ROI Per Trade",
    "Weekly ROI",
    "Stock-Hold Day",
    "Daily Risk",
    "Weekly Risk",
    "Monthly Risk",
    "Yearly Risk",
    "Buy Count",
    "Sell Count",
    "Trade Count",
    "Stock / Asset Rate",
    "Stock / Asset Change Std",
    "Date From",
    "Date To",
    "Initial Money",
    "Model Update Time",
    "Model Version",
    "Test Time"
]

class TraderRecorder():
    '''Record the Trader result'''

    def _getFromattedTime(self):
        '''回傳現在格式化的時間，ex. 2015/03/06 17:25:16 '''
        t = datetime.now()
        return (str(t.year)+'/'+str(t.month).zfill(2)+'/'+'/'+str(t.day).zfill(2)+' '+
            str(t.hour).zfill(2)+':'+str(t.minute).zfill(2)+':'+str(t.second).zfill(2))

    def _getBuyAndSellSeries(self, close_series, trade_series):
        '''為了做成買賣趨勢圖，把交易序列和價格序列，各轉換為一個序列，有買賣就放值，沒買賣就放 None'''
        buy_series = []
        sell_series = []

        for i in range(len(close_series)):
        
            if trade_series[i] == 1:
                buy_series.append(close_series[i])
            else:
                buy_series.append(None)

            if trade_series[i] == -1:
                sell_series.append(close_series[i])
            else:
                sell_series.append(None)

        return buy_series, sell_series

    def _recordToCSV(self, folder, filename, col1, row):
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

    def _recordToPNG(self, result):
        '''輸出買賣過程的圖檔，以當天收盤價當作約略的點，紅色的三角形是買入，藍色正方形是賣出'''
        # 輸出買賣圖檔
        x_axis = range(len(result["Close Series"]))

        buy_series, sell_series = self._getBuyAndSellSeries(result["Close Series"],\
                                                            result["Trade Series"])
        
        plt.plot(x_axis, result["Close Series"], c='#000000', ls='-', lw=0.2)
        plt.plot(x_axis, buy_series, c='#ff0000', marker='o', ms=5, alpha=0.5)
        plt.plot(x_axis, sell_series, c='#0000ff', marker='s', ms=5, alpha=0.5)

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
        
    def record(self, result):
        '''把 Treader 的結果記錄下來'''
        row = [
            str(result["ROI"])+'%',
            str(result["ROI Per Trade"])+'%',
            str(result["Weekly ROI"])+'%',
            round(result["Stock-Hold Day"], 3),
            round(result["Daily Risk"], 3),
            round(result["Weekly Risk"], 3),
            round(result["Monthly Risk"], 3),
            round(result["Yearly Risk"], 3),
            result["Buy Count"],
            result["Sell Count"],
            result["Trade Count"],
            round(result["Stock / Asset Rate"], 3),
            round(result["Stock / Asset Change Std"], 3),
            result["Date From"],
            result["Date To"],
            result["Initial Money"],
            result["Update Time"],
            result["Model Version"],
            self._getFromattedTime()
        ]

        self._recordToCSV(MODEL_RESULT_PATH, result["Model Description"], result["Stock Number"], row)
        self._recordToCSV(STOCK_RESULT_PATH, result["Stock Number"], result["Model Description"], row)
        
        self._recordToPNG(result)