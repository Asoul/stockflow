#!/bin/python
# -*- coding: utf-8 -*-

import csv
from config import *
from os import listdir
from Reader import Reader
from Trader import Trader
from datetime import date, timedelta
from TraderRecorder import TraderRecorder
from CandleDrawer import CandleDrawer

class Tester():
    '''To Test models'''
    # 輸入 model, target year, 要不要輸出圖檔, 要不要輸出 csv 檔, 股票清單, 要不要每日交易資訊, 交易模式
    # 輸出 csv 檔, 圖片(用 Drawer), 計算ROI的年份

    def __init__(self, numbers, Model):
        # check the number from Database
        tsecNumbers = [ n[:-4] for n in listdir(TSEC_DATA_PATH) if n[-4:] == '.csv' ]
        for number in numbers:
            if number not in tsecNumbers:
                numbers.remove(number)

        self.numbers = numbers
        self.Model = Model

    def run(self, mode = 'train', noLog = False, noRecord = False, dateFrom = None, dateTo = None, roiThr = -100):

        for number in self.numbers:

            reader = Reader(number)

            model = self.Model()
            trader = Trader(model.infos, number)

            
            while True:
                row = reader.getInput()
                if row == None: break
                last_row = row

                prediction = model.predict()
                
                today = date(int(row[0].split('/')[0])+1911,
                             int(row[0].split('/')[1]),
                             int(row[0].split('/')[2]))

                if (dateFrom != None and (today - dateFrom).days < 0 or
                    dateTo != None and (today - dateTo).days > 0):
                    
                    model.update(row, None)
                else:
                    trade = trader.do(row, prediction)
                    if mode == 'train' and not noLog and trade['Volume'] != 0:
                        print ('%d %s %d at %.2f, Money: %d, Stock: %d, Asset: %d, Rate: %.3f%%' % (
                            trade['Day'], trade['Act'], trade['Volume'], trade['Value'], 
                            trade['Money'], trade['Stock'], trade['Asset'], trade['Rate']))
                    
                    model.update(row, trade)
            
            result = trader.analysis()
            if mode == 'tmrGood' and result["ROI"] > roiThr:
                print last_row[0], number, ' at ', float(last_row[6]), '該買囉, ROI 累計：', result["ROI"], '%'

            if mode == 'train' and not noRecord:
                tr = TraderRecorder()
                tr.record(result)

                
    def drawCandle(self):
        drawer = CandleDrawer()
        for number in self.numbers:
            drawer.draw(number)

    # def drawMA(self):

    # def drawSimple(self):

    # def predict(self, min_roi = 0.0, ):
        