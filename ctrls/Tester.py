#!/bin/python
# -*- coding: utf-8 -*-

import csv
import json
from config import *
import requests
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

    def printTrade(self, trade):
        print ('Day %d, %s %d at %.2f, Money: %d, Stock: %d, Asset: %d, Rate: %.3f%%' % 
            (trade['Day'], trade['Act'], trade['Volume'], trade['Value'], 
            trade['Money'], trade['Stock'], trade['Asset'], trade['Rate'])
        )

    def getTmpData(self, number):

        page = requests.get('http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_'+number+'.tw&json=1&delay=0')
        content = json.loads(page.content)
        vals = content['msgArray'][0]
        t = date.today()
        return [str(t.year-1911)+'/'+str(t.month).zfill(2)+'/'+str(t.day).zfill(2),
                vals['v'], 0, vals['o'], vals['h'], vals['l'], vals['z'], 0, 0]

    def notInPeriod(self, row, dateFrom, dateTo):

        data_day = date(int(row[0].split('/')[0])+1911, 
                        int(row[0].split('/')[1]),
                        int(row[0].split('/')[2]))

        if dateFrom and (data_day - dateFrom).days < 0:
            return False
        elif dateTo and (data_day - dateTo).days > 0:
            return False
        else:
            return True

    def run(self, mode = 'train', noLog = False, noRecord = False, dateFrom = None, dateTo = None, roiThr = -100, drawCandle = True):
        '''noLog 和 noRecord 只對 train 模式有用，其他模式一律預設不會輸出，
            drawCandle 預設是 True，
        '''
        # tmpFlag 會用 api 抓最新資料
        if mode == 'tmpGood' or mode == 'tmpHold': tmpFlag = True
        else: tmpFlag = False

        # Run for each stock number
        for number in self.numbers:

            reader = Reader(number)
            model = self.Model()
            trader = Trader(model.infos, number)
            
            while True:
                row = reader.getInput()
                if row == None:
                    if tmpFlag:
                        row = self.getTmpData(number)
                        tmpFlag = False
                    else: break

                last_row = row

                prediction = model.predict()
                
                if (dateFrom or dateTo) and self.notInPeriod(row, dateFrom, dateTo):
                    model.update(row, None)
                else:
                    trade = trader.do(row, prediction)
                    model.update(row, trade)

                    if mode == 'train' and not noLog and trade['Volume'] != 0: self.printTrade(trade)
            
            result = trader.analysis()

            if mode == 'train' and not noRecord:
                tr = TraderRecorder()
                tr.record(result)

            elif result["ROI"] > roiThr:
                print last_row[0], number, ' at ', float(last_row[6]), '該買囉, ROI 累計：', result["ROI"], '%'
                if drawCandle:
                    CandleDrawer().draw(result)

            

        