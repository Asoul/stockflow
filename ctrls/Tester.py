#!/bin/python
# -*- coding: utf-8 -*-

import csv
import json
import requests
from ctrls import *
from settings import *
from os import listdir
from datetime import date

class Tester():
    '''To Test models'''

    def __init__(self, numbers, Model):
        # check the number from Database, remove error numbers
        tsecNumbers = [ n[:-4] for n in listdir(TSEC_DATA_PATH) if n[-4:] == '.csv' ]
        for number in numbers:
            if number not in tsecNumbers:
                numbers.remove(number)

        self.numbers = numbers
        self.Model = Model

    def _getTmpData(self, number):

        page = requests.get('http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_'+number+'.tw&json=1&delay=0')
        content = json.loads(page.content)
        vals = content['msgArray'][0]
        t = date.today()
        return [str(t.year-1911)+'/'+str(t.month).zfill(2)+'/'+str(t.day).zfill(2),
                vals['v'], 0, vals['o'], vals['h'], vals['l'], vals['z'], 0, 0]

    def _notInPeriod(self, row, dateFrom, dateTo):

        data_day = date(int(row[0].split('/')[0])+1911, 
                        int(row[0].split('/')[1]),
                        int(row[0].split('/')[2]))

        if dateFrom and (data_day - dateFrom).days < 0:
            return True
        elif dateTo and (data_day - dateTo).days > 0:
            return True
        else:
            return False

    def getROI(self, result):
        if len(result["Asset Series"]) > 0:
            return str(round((float(result["Asset Series"][-1])/result["Asset Series"][0] - 1)*100, 3)) + '%'
        else:
            return "0.000 %"

    def run(self, mode = 'train', noLog = False, noRecord = False, dateFrom = None, dateTo = None, roiThr = -100, drawCandle = True):
        '''
            noLog 和 noRecord 只對 train 模式有用，其他模式一律預設不會輸出，
            drawCandle 只對非 train 模式有用，避免一次輸出太多圖檔，跑得很慢
        '''
        # tmpFlag 會用 api 抓最新資料
        if mode == 'tmpGood' or mode == 'tmpHold': master_tmp_flag = True
        else: master_tmp_flag = False
        for number in self.numbers:

            reader = Reader(number)
            model = self.Model()
            trader = Trader(model.infos, number, noLog)

            tmp_flag = master_tmp_flag
            
            while True:
                row = reader.getInput()
                if row == None:
                    if tmp_flag:
                        row = self._getTmpData(number)
                        tmp_flag = False
                    else: break

                last_row = row

                if (dateFrom or dateTo) and self._notInPeriod(row, dateFrom, dateTo):
                    model.updateData(row)
                else:
                    # 更新 Trader 資訊
                    trader.updateData(row)

                    # 開盤的買：用開盤價交易
                    order = model.predict('start', float(row[3]))
                    trade = trader.place('start', order)
                    model.updateTrade(trade)

                    # 開盤後，盤中掛單
                    order = model.predict('mid', float(row[3]))
                    trade = trader.place('mid', order)
                    model.updateTrade(trade)

                    # 盤末的更新
                    model.updateData(row)

                    # 收盤的買：用收盤價交易
                    order = model.predict('end', float(row[6]))
                    trade = trader.place('end', order)
                    model.updateTrade(trade)
            
            result = trader.getResult()

            if mode == 'train' and not noRecord:
                tr = TraderRecorder()
                tr.record(result)

            elif mode == 'tmpGood' or mode == 'tmrGood':

                # Model 預測出要買，而且指定時間內累計 ROI 高於 ROI Threshold
                if order["Type"] == 'Buy' and result["ROI"] > roiThr:
                    print last_row[0], number, ' at ', float(last_row[6]), '該買囉, ROI 累計：', self.getROI(result)
                    
                    # 預設買前看一下 CandleStick 確定一下
                    if drawCandle: CandleDrawer().draw(number)

            elif mode == 'tmpHold' or mode == 'tmrHold':
                if order["Type"] == 'Sell':
                    print last_row[0], number, ' at ', float(last_row[6]), '該賣囉, ROI 累計：', self.getROI(result)
                elif order["Type"] == 'Nothing':
                    print last_row[0], number, ' at ', float(last_row[6]), '不要動, ROI 累計：', self.getROI(result)

                # 做操作前看一下 CandleStick 確定一下
                if drawCandle: CandleDrawer().draw(number)