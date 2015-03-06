#!/bin/python
# -*- coding: utf-8 -*-

import csv
from config import *
from Reader import Reader
from Trader import Trader
from TraderRecorder import TraderRecorder

class Tester():
    '''To Test models'''
    # 輸入 model, target year, 要不要輸出圖檔, 要不要輸出 csv 檔, 股票清單, 要不要每日交易資訊, 交易模式
    # 輸出 csv 檔, 圖片(用 Drawer), 計算ROI的年份, 

    def __init__(self, numbers, Model):
        self.numbers = numbers
        self.Model = Model
    

    def train(self, noLog = False, noRecord = False):
        for number in self.numbers:
            reader = Reader(number)
            model = self.Model()
            trader = Trader(model.infos, number)
            
            
            while True:
                row = reader.getInput()
                if row == None: break

                model.update(row)

                prediction = model.predict()
                
                trade = trader.do(float(row[6]), prediction)
                if trade[5] != 0 and not noLog: print trade
            
            if not noRecord:
                tr = TraderRecorder()
                tr.record(trader.analysis())

    # def predict(self, min_roi = 0.0, ):
        