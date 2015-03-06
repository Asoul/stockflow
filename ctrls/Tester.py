#!/bin/python
# -*- coding: utf-8 -*-

import csv
from config import *
from os import listdir
from Reader import Reader
from Trader import Trader
from TraderRecorder import TraderRecorder
from CandleDrawer import CandleDrawer

class Tester():
    '''To Test models'''
    # 輸入 model, target year, 要不要輸出圖檔, 要不要輸出 csv 檔, 股票清單, 要不要每日交易資訊, 交易模式
    # 輸出 csv 檔, 圖片(用 Drawer), 計算ROI的年份

    def __init__(self, numbers, Model):
        tsecNumbers = [ n[:-4] for n in listdir(TSEC_DATA_PATH) if n[-4:] == '.csv' ]
        for number in numbers:
            if number not in tsecNumbers:
                numbers.remove(number)
        self.numbers = numbers
        self.Model = Model

    def train(self, noLog = False, noRecord = False, dateFrom = None, dateTo = None):

        for number in self.numbers:

            model = self.Model()
            reader = Reader(number)
            if reader == None:
                print 'No File Error'
                continue

            trader = Trader(model.infos, number)
            
            while True:
                row = reader.getInput()
                if row == None: break

                prediction = model.predict()
                
                trade = trader.do(row, prediction)
                if trade['Volume'] != 0 and not noLog:
                    print ('%d %s %d at %.2f, Money: %d, Stock: %d, Asset: %d, Rate: %.3f%%' % (
                        trade['Day'], trade['Act'], trade['Volume'], trade['Value'], 
                        trade['Money'], trade['Stock'], trade['Asset'], trade['Rate']))

                model.update(row, trade)
            
            if not noRecord:
                tr = TraderRecorder()
                tr.record(trader.analysis())

    # def predict(self, )
        
    def drawCandle(self):
        drawer = CandleDrawer()
        for number in self.numbers:
            drawer.draw(number)

    # def drawMA(self):

    # def drawSimple(self):

    # def predict(self, min_roi = 0.0, ):
        